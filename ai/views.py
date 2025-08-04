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

    def post(self, request):
        # Embed question for matching
        pass


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


# same code to parse_ai_suggestion_to_json.py
def parse_ai_suggestion_to_json(raw_data):
    # Parse into desired format
    ability_set = {}
    activity_list = []

    for item in raw_data:
        content_lines = item["content"].split("\n")
        activity_name = ""
        description = ""
        position = ""
        event_role = ""
        event_categories = []

        for line in content_lines:
            if line.startswith("Name:"):
                activity_name = line.replace("Name:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
            elif line.startswith("Position:"):
                position = line.replace("Position:", "").strip()
            elif line.startswith("Event Role:"):
                event_role = line.replace("Event Role:", "").strip()
            elif line.startswith("Event Category:"):
                categories = line.replace("Event Category:", "").strip().split(",")
                event_categories = [c.strip() for c in categories]
                for cat in event_categories:
                    ability_set[cat] = (
                        f"{cat} 관련 경험과 문제 해결에 대한 적용 능력을 보여줍니다."  # placeholder desc
                    )

        activity_list.append(
            {
                "id": item["id"],
                "activity": activity_name,
                "fit": round(item["similarity"], 3),
                "events_list": [{"id": f"{item['id']}-event", "event": event_role}],
            }
        )

    # Build final structure
    parsed_result = {
        "ability_list": [
            {"id": idx + 1, "ability": ability, "description": desc}
            for idx, (ability, desc) in enumerate(ability_set.items())
        ],
        "activity_list": activity_list,
    }

    # Show output
    parsed_result_json = json.dumps(parsed_result, ensure_ascii=False, indent=2)
    return parsed_result_json


@csrf_exempt
def analyze_question(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract required fields
        application_id = data.get("application_id")
        question_id = data.get("question_id")
        question = data.get("question")

        # Validate required fields
        if not all([application_id, question_id, question]):
            return JsonResponse(
                {
                    "error": "Missing required fields. Please provide application_id, question_id, and question"
                },
                status=400,
            )

        ###################### Embedding #########################################################
        # dummy data already embedded in supabase with embed_my_log.py and filter_json.py
        # same code as ask_question.py
        tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
        env = environ.Env()

        environ.Env.read_env(env_file=os.path.join(os.path.dirname(__file__), ".env"))
        # print(os.path.join(os.path.dirname(__file__), ".env"))

        SUPABASE_URL = env("DB_URL")
        SUPABASE_KEY = env("DB_KEY")

        client = OpenAI(api_key=env("OPENAI_KEY"))
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        embedding_response = client.embeddings.create(
            input=question,
            model="text-embedding-3-small",
        )
        query_embedding = embedding_response.data[0].embedding
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.3,
                "match_count": 3,
            },
        ).execute()

        # print(response.data)
        # Prepare the response
        # response_data = {"ability_list": ability_list, "activity_list": activity_list}
        parsed_result_json = json.loads(
            parsed_result_json
        )  # json 형태로 불러오기 위해서
        response_data = {
            "ability_list": parsed_result_json["ability_list"],
            "activity_list": parsed_result_json["activity_list"],
        }

        return JsonResponse(response_data, status=200, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def chunk_text(text, max_tokens=8000):
    tokens = tokenizer.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + max_tokens]
        chunks.append(tokenizer.decode(chunk))
        i += max_tokens
    return chunks
