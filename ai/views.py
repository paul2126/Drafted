from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import EventSuggestion
from applications.models import QuestionList
from activities.models import Activity, Event
from openai import OpenAI
import environ
import tiktoken
from supabase import create_client, Client
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from utils.supabase_utils import get_supabase_client, get_user_id_from_token

tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
environ.Env.read_env(env_file=os.path.join(settings.BASE_DIR, ".env"))
env = environ.Env()
client = OpenAI(api_key=env("OPENAI_KEY"))


def _convert_to_paragraph(prompt_path, data):
    """Convert text to paragraph format for embedding based on prompt requirements"""
    try:
        prompt = ""
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read().strip()
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"{data}",
            instructions=f"{prompt}",
        )
        return response.output_text
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return ""


def _check_embedding_status(supabase, user_id):
    # Get all user events with their embedding status in one query
    events_with_embeddings = (
        supabase.table("event")
        .select(
            """
            id, updated_at,
            activity!inner(user_id),
            activity_embedding(event_id, updated_at)
        """
        )
        .eq("activity.user_id", user_id)
        .execute()
    )
    print(f"Total events found: {(events_with_embeddings.data)}")
    insert_event_ids = []
    update_event_ids = []
    for event in events_with_embeddings.data:
        embedding = event.get("activity_embedding")
        if not embedding:
            # No embedding exists
            insert_event_ids.append(event["id"])
        elif event["updated_at"] > embedding[0]["updated_at"]:
            # Event updated since last embedding
            update_event_ids.append(event["id"])
    print(f"Events needing insert: {insert_event_ids}")
    print(f"Events needing update: {update_event_ids}")
    return {"insert": insert_event_ids, "update": update_event_ids}


class GenerateEmbeddingsView(APIView):
    """Generate embeddings for user's activity+event chunks"""

    @swagger_auto_schema(
        operation_summary="Generate Activity Embeddings",
        operation_description="Generate embeddings for all user activities and events",
        responses={200: "Embeddings generated successfully", 400: "Bad Request"},
        tags=["AI Embeddings"],
    )
    def post(self, request):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Get all activities with their events
            activities_result = (
                supabase.table("activity")
                .select(
                    "id, activity_name, category, position, description, start_date, end_date, "
                    "event!activity_id(id, event_name, situation, task, action, result, contribution, start_date, end_date)"
                )
                .eq("user_id", user_id)
                .execute()
            )

            if not activities_result.data:
                return Response(
                    {"message": "No activities found for user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Compute event ids that need embedding
            need_embedding_ids = _check_embedding_status(supabase, user_id)

            # ids that needs insert
            need_insert_ids = need_embedding_ids["insert"]
            # ids that needs update
            need_update_ids = need_embedding_ids["update"]

            if not need_insert_ids and not need_update_ids:
                return Response(
                    {"message": "No new embeddings to generate"},
                    status=status.HTTP_200_OK,
                )

            # Remove already embedded events from activities
            activities_result.data = [
                activity
                for activity in activities_result.data
                if any(
                    event["id"] in need_insert_ids + need_update_ids
                    for event in activity.get("event", [])
                )
            ]
            print(activities_result.data)
            generated_count = 0

            # Process each activity
            for activity in activities_result.data:
                events = activity.get("event", [])

                # Create embedding for each activity+event pair
                for event in events:
                    json_data = self._convert_to_json(activity, event)
                    paragraph = _convert_to_paragraph(
                        prompt_path="./ai/prompts/activity-paragraph.txt",
                        data=json_data,
                    )
                    print(json_data)
                    print(paragraph)
                    embedding = self._generate_embedding(paragraph)
                    self._save_embedding(
                        supabase, user_id, event, embedding, cmd="insert"
                    )
                    generated_count += 1

            return Response(
                {
                    "message": f"Successfully generated {generated_count} embeddings",
                    "count": generated_count,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to generate embeddings", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _convert_to_json(self, activity, event=None):
        """Convert activity and event data to structured JSON format"""
        # Build activity JSON structure
        activity_json = {
            "favorite": activity.get("favorite", False),
            "activity_name": activity.get("activity_name", ""),
            "category": activity.get("category", ""),
            "position": activity.get("position", ""),
            "file_list": activity.get("file_list", []),
            "start_date": activity.get("start_date", ""),
            "end_date": activity.get("end_date", ""),
            "description": activity.get("description", ""),
            "keywords": activity.get("keywords", []),
            "events": [],
        }

        # If event is provided, add it to events array
        if event:
            event_json = {
                "event_name": event.get("event_name", ""),
                "start_date": event.get("start_date", ""),
                "end_date": event.get("end_date", ""),
                "result": event.get("result", ""),
                "situation": event.get("situation", ""),
                "task": event.get("task", ""),
                "action": event.get("action", ""),
                "contribution": event.get("contribution", ""),
            }
            activity_json["events"].append(event_json)
        else:
            # If processing activity without specific event, get all events for this activity
            events = activity.get("event", [])
            for evt in events:
                event_json = {
                    "event_name": evt.get("event_name", ""),
                    "start_date": evt.get("start_date", ""),
                    "end_date": evt.get("end_date", ""),
                    "result": evt.get("result", ""),
                    "situation": evt.get("situation", ""),
                    "task": evt.get("task", ""),
                    "action": evt.get("action", ""),
                    "contribution": evt.get("contribution", ""),
                }
                activity_json["events"].append(event_json)
        return json.dumps(activity_json, ensure_ascii=False, indent=2)

    def _generate_embedding(self, text):
        """Generate embedding using OpenAI API"""
        response = client.embeddings.create(model="text-embedding-3-small", input=text)

        return response.data[0].embedding

    def _save_embedding(self, supabase, user_id, event, embedding, cmd="insert"):
        """Save embedding to database"""
        embedding_data = {
            "user_id": user_id,
            "event_id": event["id"] if event else None,
            "metadata": {},
            "embedding": embedding,
        }
        if cmd == "update":
            # Update existing embedding
            embedding_data["updated_at"] = event["updated_at"]
            result = (
                supabase.table("activity_embedding")
                .update(embedding_data)
                .eq("event_id", event["id"])
                .eq("user_id", user_id)
                .execute()
            )
        else:
            # Save to activity_embedding table
            result = (
                supabase.table("activity_embedding").insert(embedding_data).execute()
            )

        if not result.data:
            raise Exception(f"Failed to save embedding for event {event['id']}")


class AnalyzeQuestionView(APIView):
    """Convert application question to embedding"""

    @swagger_auto_schema(
        operation_summary="Analyze Application Question",
        operation_description="Analyze application question and find matching activities",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "question": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Application question to analyze",
                )
            },
            required=["question"],
        ),
        responses={
            200: "Matching activities found",
            400: "Bad Request",
            500: "Internal Server Error",
        },
        tags=["AI Question Analysis"],
    )
    def post(self, request):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)
            print(request.data)

            # Get question from application table
            question = (
                supabase.table("question_list")
                .select("application!inner(user_id), question")
                .eq("application.user_id", user_id)
                .eq("id", request.data.get("question_id"))
                .execute()
            )
            print(question.data)

            question_paragraph = _convert_to_paragraph(
                prompt_path="./ai/prompts/question-paragraph.txt",
                data=question.data[0]["question"],
            )
            print(question_paragraph)
            embedding_response = client.embeddings.create(
                input=question_paragraph,
                model="text-embedding-3-small",
            )
            # save emebedding to question_list table question_explanation
            question_list = (
                supabase.table("question_list")
                .update({"question_explanation": question_paragraph})
                .eq("id", request.data.get("question_id"))
                .execute()
            )
            query_embedding = embedding_response.data[0].embedding
            response = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,  # 1536-dimensional vector
                    "match_threshold": 0.3,  # Minimum similarity score
                    "match_count": 3,  # Maximum results to return
                },
            ).execute()
            print(response)
            print(response.data)
            return Response(
                {
                    "message": "Question analyzed successfully",
                    "data": question_paragraph,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class EventSuggestionsView(APIView):
    """Find matching Event for question"""

    def post(self, request):
        # Vector similarity search
        pass


class ChatSessionView(APIView):
    """Manage chat sessions for personal statement help"""

    def get(self, request):
        # List user's chat sessions
        pass

    def post(self, request):
        # Create new chat session
        pass


class ChatMessageView(APIView):
    """Send messages in chat session"""

    def post(self, request, session_id):
        # Send message, get AI response
        pass


# Uncomment if you want to chunk text for embedding
# def chunk_text(text, max_tokens=8000):
#     tokens = tokenizer.encode(text)
#     chunks = []
#     i = 0
#     while i < len(tokens):
#         chunk = tokens[i : i + max_tokens]
#         chunks.append(tokenizer.decode(chunk))
#         i += max_tokens
#     return chunks


##############################application views 를 위한 임시###################
# for applications 2-1
@csrf_exempt
def generate_question_guideline(request):
    """
    지원서 문항에 대한 '작성 가이드라인'을 AI로 생성 (현재 Mock)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question = data.get("question", "")

        if not question:
            return JsonResponse({"error": "question is required"}, status=400)

        # Mock response - replace with actual AI call
        response = {
            "question_id": data.get("question_id", 0),
            "content": (
                f"문항 '{question[:15]}...'은 개인 동기와 경험을 연결하여 "
                f"지원 동기의 진정성과 실행 의지를 드러내는 것이 효과적입니다. "
                f"구체적인 프로젝트 경험, 자발적 활동, 실무 체험을 포함하면 좋습니다."
            ),
        }

        return JsonResponse(response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


# for 2-2 . get: 문항별 AI 추천 활동 5개


@csrf_exempt
def recommend_events(request):
    """
    AI: 문항별 추천 활동 5개 + 문항 분석 결과 반환 (Mock 버전)
    출력: analysis(문항 분석), suggested_events(추천 이벤트), tip(작성 팁)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id", 0)
        question = data.get("question", "")

        # Mock response - replace with actual AI call
        ai_result = {
            "analysis": f"문항 '{question[:15]}...'은 문제 해결력과 실행력을 평가합니다.",
            "suggested_events": [
                {
                    "activity_name": "패스트캠퍼스",
                    "event_name": "서비스기획(PM) 온라인 교육 수강",
                    "situation": "PM 관련 교육 수강 경험",
                    "task": "실제 프로젝트 기반 과제 수행",
                    "action": "문제 정의 및 개선 아이디어 제안",
                    "result": "개발 역량과 문제 해결력 강화",
                    "contribution": 90.0,
                    "comment": "서비스 개발 관심과 실행력을 보여주는 이벤트입니다.",
                },
                {
                    "activity_name": "멋쟁이사자처럼",
                    "event_name": "해커톤 프로젝트",
                    "situation": "팀 해커톤에서 웹서비스 개발",
                    "task": "백엔드 개발 담당",
                    "action": "API 설계 및 구현",
                    "result": "최우수상 수상",
                    "contribution": 85.0,
                    "comment": "실무 개발 경험과 협업 능력을 강조할 수 있습니다.",
                },
                {
                    "activity_name": "대학신문 활동",
                    "event_name": "사설 프로세스 개선",
                    "situation": "편집장으로서 프로세스 문제 인식",
                    "task": "문제 진단 및 개선안 설계",
                    "action": "새로운 제작 프로세스 도입",
                    "result": "오류율 50% 감소",
                    "contribution": 80.0,
                    "comment": "문제 해결 과정이 잘 드러납니다.",
                },
            ],
            "tip": "이런 활동들을 중심으로 문항을 구성하면 문제 해결력과 실행력이 더 명확하게 드러납니다.",
        }

        return JsonResponse(ai_result, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


# for 3-1. get: 문항별 작성 가이드라인
@csrf_exempt
def generate_editor_guideline(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id", 0)
        # Mock response - replace with actual AI call
        dummy_response = {
            "question_id": question_id,
            "content": (
                "### 1. 관점 설정\n"
                "단순히 활동이 좋았다는 것이 아니라, 문제의식과 동기를 설명하세요.\n\n"
                "### 2. 경험 연결\n"
                "활동과 과거 경험을 구체적으로 연결하여 작성하세요.\n\n"
                "### 3. 해당 활동의 의미\n"
                "활동에서의 역할과 성과를 강조하세요.\n\n"
                "### 4. 구체적인 목표와 열정 강조\n"
                "앞으로의 목표와 실행 의지를 드러내세요."
            ),
        }

        return JsonResponse(dummy_response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


# for 3-1. get: 문항별 작성 가이드라인
@csrf_exempt
def editor_guideline(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id", 0)
        # Mock response - replace with actual AI call
        dummy_response = {
            "question_id": question_id,
            "content": (
                "### 1. 관점 설정\n"
                "단순히 활동이 좋았다는 것이 아니라, 문제의식과 동기를 설명하세요.\n\n"
                "### 2. 경험 연결\n"
                "활동과 과거 경험을 구체적으로 연결하여 작성하세요.\n\n"
                "### 3. 해당 활동의 의미\n"
                "활동에서의 역할과 성과를 강조하세요.\n\n"
                "### 4. 구체적인 목표와 열정 강조\n"
                "앞으로의 목표와 실행 의지를 드러내세요."
            ),
        }

        return JsonResponse(dummy_response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


# for 3-1. get: 문항별 작성 가이드라인
@csrf_exempt
def editor_guideline(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id", 0)
        # Mock response - replace with actual AI call
        dummy_response = {
            "question_id": question_id,
            "content": (
                "### 1. 관점 설정\n"
                "단순히 활동이 좋았다는 것이 아니라, 문제의식과 동기를 설명하세요.\n\n"
                "### 2. 경험 연결\n"
                "활동과 과거 경험을 구체적으로 연결하여 작성하세요.\n\n"
                "### 3. 해당 활동의 의미\n"
                "활동에서의 역할과 성과를 강조하세요.\n\n"
                "### 4. 구체적인 목표와 열정 강조\n"
                "앞으로의 목표와 실행 의지를 드러내세요."
            ),
        }

        return JsonResponse(dummy_response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


###############################################################
