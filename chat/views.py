from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.supabase_utils import get_supabase_client, get_user_id_from_token
from openai import OpenAI
import os
import environ
from django.conf import settings


environ.Env.read_env(env_file=os.path.join(settings.BASE_DIR, ".env"))
env = environ.Env()
client = OpenAI(api_key=env("OPENAI_KEY"))


def _generate_ai_response(supabase, session_id, user_message, user_id):
    """Generate AI response using OpenAI"""
    try:
        # Get conversation history (last 10 messages for context)
        history_result = (
            supabase.table("chat_message")
            .select("role, content")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant specialized in helping users write personal statements "
                    "and application essays. You can help with brainstorming, structuring content, "
                    "improving writing, and providing feedback. Be supportive, constructive, and specific "
                    "in your responses."
                ),
            }
        ]

        # Add conversation history (reverse to get chronological order)
        for msg in reversed(history_result.data):
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response using OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again."


class ChatSessionView(APIView):
    """Manage chat sessions for personal statement help"""

    @swagger_auto_schema(
        operation_summary="Get User Chat Sessions",
        operation_description="Retrieve all chat sessions for the authenticated user",
        responses={
            200: openapi.Response(
                description="Chat sessions retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "sessions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "message_count": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
        tags=["AI Chat"],
    )
    def get(self, request):
        """List user's chat sessions"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Get chat sessions with message count
            sessions_result = (
                supabase.table("chat_session")
                .select("id, title, created_at, updated_at")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .execute()
            )

            sessions = []
            for session in sessions_result.data:
                # Get message count for each session
                message_count_result = (
                    supabase.table("chat_message")
                    .select("id", count="exact")
                    .eq("session_id", session["id"])
                    .execute()
                )

                session["message_count"] = message_count_result.count or 0
                sessions.append(session)

            return Response(
                {"sessions": sessions},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to retrieve chat sessions", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Create New Chat Session",
        operation_description="Create a new chat session for the user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Title for the chat session (optional)",
                ),
                "initial_message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Initial message to start the conversation (optional)",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Chat session created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "session_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "title": openapi.Schema(type=openapi.TYPE_STRING),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            )
        },
        tags=["AI Chat"],
    )
    def post(self, request):
        """Create new chat session"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            title = request.data.get(
                "title",
                f"Chat Session {self._get_session_count(supabase, user_id) + 1}",
            )
            initial_message = request.data.get("initial_message")

            # Create new chat session
            session_data = {
                "user_id": user_id,
                "title": title,
            }

            session_result = (
                supabase.table("chat_session").insert(session_data).execute()
            )

            if not session_result.data:
                raise Exception("Failed to create chat session")

            session_id = session_result.data[0]["id"]

            # If initial message provided, add it and get AI response
            if initial_message:
                self._add_message(supabase, session_id, "user", initial_message)
                ai_response = _generate_ai_response(
                    supabase, session_id, initial_message, user_id
                )
                self._add_message(supabase, session_id, "assistant", ai_response)

            return Response(
                {
                    "session_id": session_id,
                    "title": title,
                    "message": "Chat session created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to create chat session", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_session_count(self, supabase, user_id):
        """Get total number of sessions for user"""
        result = (
            supabase.table("chat_session")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return result.count or 0

    def _add_message(self, supabase, session_id, role, content):
        """Add a message to the chat session"""
        message_data = {
            "session_id": session_id,
            "role": role,
            "content": content,
        }

        result = supabase.table("chat_message").insert(message_data).execute()

        if not result.data:
            raise Exception("Failed to save message")

        return result.data[0]


class ChatMessageView(APIView):
    """Send messages in chat session"""

    @swagger_auto_schema(
        operation_summary="Get Chat Messages",
        operation_description="Retrieve all messages from a chat session",
        responses={
            200: openapi.Response(
                description="Messages retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "messages": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "role": openapi.Schema(type=openapi.TYPE_STRING),
                                    "content": openapi.Schema(type=openapi.TYPE_STRING),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
        tags=["AI Chat"],
    )
    def get(self, request, session_id):
        """Get all messages from a chat session"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Verify session belongs to user
            session_result = (
                supabase.table("chat_session")
                .select("id")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not session_result.data:
                return Response(
                    {"error": "Chat session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get all messages for the session
            messages_result = (
                supabase.table("chat_message")
                .select("id, role, content, created_at")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .execute()
            )

            return Response(
                {"messages": messages_result.data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to retrieve messages", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Send Chat Message",
        operation_description="Send a message and get AI response",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User message content",
                ),
            },
            required=["message"],
        ),
        responses={
            200: openapi.Response(
                description="Message sent and AI response received",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user_message": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "content": openapi.Schema(type=openapi.TYPE_STRING),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "ai_response": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "content": openapi.Schema(type=openapi.TYPE_STRING),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            )
        },
        tags=["AI Chat"],
    )
    def post(self, request, session_id):
        """Send message, get AI response"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            message_content = request.data.get("message")
            if not message_content:
                return Response(
                    {"error": "Message content is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify session belongs to user
            session_result = (
                supabase.table("chat_session")
                .select("id, title")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not session_result.data:
                return Response(
                    {"error": "Chat session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Save user message
            user_message = self._add_message(
                supabase, session_id, "user", message_content
            )

            # Generate AI response
            ai_response_content = _generate_ai_response(
                supabase, session_id, message_content, user_id
            )

            # Save AI response
            ai_message = self._add_message(
                supabase, session_id, "assistant", ai_response_content
            )

            # Update session updated_at
            supabase.table("chat_session").update({"updated_at": "now()"}).eq(
                "id", session_id
            ).execute()

            return Response(
                {
                    "user_message": {
                        "id": user_message["id"],
                        "content": user_message["content"],
                        "created_at": user_message["created_at"],
                    },
                    "ai_response": {
                        "id": ai_message["id"],
                        "content": ai_message["content"],
                        "created_at": ai_message["created_at"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to send message", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _add_message(self, supabase, session_id, role, content):
        """Add a message to the chat session"""
        message_data = {
            "session_id": session_id,
            "role": role,
            "content": content,
        }

        result = supabase.table("chat_message").insert(message_data).execute()

        if not result.data:
            raise Exception("Failed to save message")

        return result.data[0]


class ChatSessionDetailView(APIView):
    """Manage individual chat session (update title, delete)"""

    @swagger_auto_schema(
        operation_summary="Update Chat Session",
        operation_description="Update chat session title",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New title for the chat session",
                ),
            },
            required=["title"],
        ),
        responses={200: "Session updated successfully"},
        tags=["AI Chat"],
    )
    def patch(self, request, session_id):
        """Update chat session title"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            new_title = request.data.get("title")
            if not new_title:
                return Response(
                    {"error": "Title is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update session title
            result = (
                supabase.table("chat_session")
                .update({"title": new_title})
                .eq("id", session_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not result.data:
                return Response(
                    {"error": "Chat session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"message": "Session title updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to update session", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Delete Chat Session",
        operation_description="Delete a chat session and all its messages",
        responses={200: "Session deleted successfully"},
        tags=["AI Chat"],
    )
    def delete(self, request, session_id):
        """Delete chat session and all messages"""
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Verify session belongs to user
            session_result = (
                supabase.table("chat_session")
                .select("id")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not session_result.data:
                return Response(
                    {"error": "Chat session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Delete all messages first
            supabase.table("chat_message").delete().eq(
                "session_id", session_id
            ).execute()

            # Delete session
            supabase.table("chat_session").delete().eq("id", session_id).execute()

            return Response(
                {"message": "Chat session deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to delete session", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
