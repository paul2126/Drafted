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

'''
class EventSuggestionsView(APIView):
    """Find matching Event for question"""

    def post(self, request):
        # Vector similarity search
        pass
'''

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


# applications app 용 ai
##############################application views 를 위한 임시 목업 결과들..###################
#for applications 2-1 


def generate_question_guideline( question,question_id: int) -> dict:
    """
    지원서 문항 가이드라인 생성
    요청(JSON):     GET /ai/application/<question_id>/guideline/?question=문항내용
    응답(JSON): { "question_id": number, "content": string }
    - 프롬프트는 `_convert_to_paragraph(prompt_path, data=...)` 한 번으로 구성
    - 모델 응답은 Strict JSON 스키마로 강제
    """
    if not question:
        return JsonResponse({"error": "question query param is required"}, status=400)

    guideline_prompt = _convert_to_paragraph(
        prompt_path="./ai/prompts/application-question-guideline.txt",
        data=json.dumps({"question_id": question_id, "question": question.strip()}, ensure_ascii=False),
    )
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",

            temperature=0.4,
            max_output_tokens=512,
            input=[{"role": "user", "content": guideline_prompt}], 
        )    
        output_text = getattr(resp, "output_text", None)
        print("resp:", resp)
        try:
            data = json.loads(output_text)
        except json.JSONDecodeError:
            # JSON이 아니면 fallback
            data = {
                "question_id": question_id,
                "content": output_text.strip()
            }
        return JsonResponse(
            {
                "question_id": int(data.get("question_id", question_id)),
                "content": (data.get("content") or "").strip(),
            },
            status=200,
        )

    except Exception as e:
        return JsonResponse(
            {"error": "AI generation failed", "detail": str(e)},
            status=502,
        )
#for 2-2 . get: 문항별 AI 추천 활동 5개
class RecommendEventsView(APIView):
    """문항 임베딩 기반 활동/이벤트 추천"""
    @swagger_auto_schema(
        operation_summary="Recommend Events for Question",
        operation_description="Find top 5 matching activities/events for a given application question",
        responses={200: "Recommended events returned"},
        tags=["AI Question Analysis"],
    )
    def get(self, request, question_id: int):
        try:
            print("🔍 [DEBUG] Start RecommendEventsView.get")
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            print(f"🔍 [DEBUG] user_id={user_id}, question_id={question_id}")
            # 질문 가져오기
            question = (
                supabase.table("question_list")
                .select("application!inner(user_id), question")
                .eq("application.user_id", user_id)
                .eq("id", question_id) 
                .execute()
            )
            print("🔍 [DEBUG] question raw response:", question)
            print("🔍 [DEBUG] question data:", getattr(question, "data", None))
            print("🔍 [DEBUG] question query result:", question.data)
            if not question.data:
                return Response({"error": "Question not found"}, status=404)

            question_text = question.data[0]["question"]
            print("🔍 [DEBUG] question_text:", question_text)
            # 질문 임베딩
            question_paragraph = _convert_to_paragraph(
                prompt_path="./ai/prompts/question-paragraph.txt",
                data=question_text,
            )
            print("🔍 [DEBUG] question_paragraph:", question_paragraph)
            embedding_response = client.embeddings.create(
                input=question_paragraph,
                model="text-embedding-3-small",
            )
            query_embedding = embedding_response.data[0].embedding
            print("🔍 [DEBUG] embedding length:", len(query_embedding))
            # 추천
            response = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.0,
                    "match_count": 2,
                },
            ).execute()
            print("🔍 [DEBUG] supabase.rpc response:", response)
            print("🔍 [DEBUG] supabase.rpc data:", getattr(response, "data", None))
            candidate_events = response.data or []
            if not candidate_events:
                return Response({"error": "No matching events"}, status=404)

            top5 = candidate_events[:2]
            print("🔍 [DEBUG] top2 candidate events:", top5)
            event_ids = [ev["event_id"] for ev in top5]
            events_detail = (
                supabase.table("event")
                .select("id, event_name, situation, task, action, result, contribution, activity_id")
                .in_("id", event_ids)
                .execute()
            )

            activity_ids = [e["activity_id"] for e in events_detail.data if e.get("activity_id")]
            activities = (
                supabase.table("activity")
                .select("id,activity_name")
                .in_("id", activity_ids)
                .execute()
            )
            events_map = {e["id"]: e for e in events_detail.data}
            activity_map = {a["id"]: a["activity_name"] for a in activities.data}

            llm_prompt = _convert_to_paragraph(
                prompt_path="./ai/prompts/application-recommend-events.txt",
                data=json.dumps({
                    "question_text": question_text,
                    "events": top5
                }, ensure_ascii=False)
            )
            print("🔍 [DEBUG] llm_prompt:",  type(llm_prompt))

            if isinstance(llm_prompt, str):
                try:
                    llm_prompt = json.loads(llm_prompt)
                except json.JSONDecodeError:
                    llm_prompt = {}   # JSON 파싱 실패 시 안전한 기본값
            elif not isinstance(llm_prompt, dict):
                llm_prompt = {}
            print("🔍 [DEBUG] llm_prompt:",  type(llm_prompt))
            print("🔍 [DEBUG] llm_prompt:",  llm_prompt)

            # 5. 최종 결과 합치기
            suggested_events = []
            for ev, com in zip(top5, llm_prompt.get("suggested_events", [])):
                detail = events_map.get(ev["event_id"], {})
                activity_name = activity_map.get(detail.get("activity_id"), "")
                suggested_events.append({
                    "activity_name": activity_name,
                    "event_id": ev["event_id"],
                    "event_name": detail.get("event_name", ""),
                    "situation": detail.get("situation", ""),
                    "task": detail.get("task", ""),
                    "action": detail.get("action", ""),
                    "result": detail.get("result", ""),
                    "contribution": detail.get("contribution", ""),
                    "similarity": ev.get("similarity", 0.0),
                    "comment": com.get("comment", "추천된 이벤트입니다."),
                })

            result = {
                "suggested_events": suggested_events,
            }
            print("[DEBUG] Final result ready:", result)

            return Response(result, status=200)

        except Exception as e:
            print("[DEBUG] Exception occurred:", str(e))
            return Response(
                {"error": "Failed to recommend events", "detail": str(e)},
                status=500,
            )


#for 3-1. get: 문항별 작성 가이드라인 

def generate_editor_guideline( question,question_id: int,event_id: int = None) -> dict:
 
    if not question:
        return JsonResponse({"error": "question query param is required"}, status=400)

    try:
        from .models import EventSuggestion

        suggestions = (
            EventSuggestion.objects
            .filter(question_id=question_id)
            .select_related("event")
        )
        if not suggestions.exists():
            event_data = None
        else:
            event_data = []
            for suggestion in suggestions:
                ev = suggestion.event
                if ev:
                    event_data.append({
                        "id": ev.id,
                        "name": ev.name,
                        "situation": ev.situation,
                        "task": ev.task,
                        "action": ev.action,
                        "result": ev.result,
                        "contribution": ev.contribution,
                    })

    except Exception as e:
        print("Event fetch error:", e)
            
    prompt_data = {
        "question_id": question_id,
        "question": question.strip(),
    }
    if event_data:
        prompt_data["events"] = event_data

    guideline_prompt = _convert_to_paragraph(
        prompt_path="./ai/prompts/application-editor-guideline.txt",
        data=json.dumps(prompt_data, ensure_ascii=False),
    )
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",

            temperature=0.4,
            max_output_tokens=512,
            input=[{"role": "user", "content": guideline_prompt}], 
        )    
        output_text = getattr(resp, "output_text", None)
        print("resp:", resp)
        try:
            data = json.loads(output_text)
        except json.JSONDecodeError:
            # JSON이 아니면 fallback
            data = {
                "question_id": question_id,
                "content": output_text.strip()
            }
        return JsonResponse(
            {
                "question_id": int(data.get("question_id", question_id)),
                "content": (data.get("content") or "").strip(),
            },
            status=200,
        )

    except Exception as e:
        return JsonResponse(
            {"error": "AI generation failed", "detail": str(e)},
            status=502,
        )

###############################################################
class EventSuggestionView(APIView):
    @swagger_auto_schema(
        operation_summary="이벤트 추천 저장",
        operation_description="여러 개의 (question, event) 매핑을 받아서 EventSuggestion에 저장합니다. "
                              "activity는 Event → Activity에서 자동으로 가져옵니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    "question": openapi.Schema(type=openapi.TYPE_INTEGER, description="문항 ID"),
                    "event": openapi.Schema(type=openapi.TYPE_INTEGER, description="이벤트 ID")
                },
                required=["question", "event"]
            ),
            example=[
                {"question": 1, "event": 5},
                {"question": 2, "event": 7}
            ]
        ),
        responses={
            201: openapi.Response(
                description="저장된 EventSuggestion 목록",
                examples={
                    "application/json": {
                        "saved": [
                            {"id": 10, "question": 1, "event": 5, "activity": "대학신문"},
                            {"id": 11, "question": 2, "event": 7, "activity": "AI 프로젝트"}
                        ]
                    }
                }
            ),
            400: "잘못된 요청",
        },
        tags=["EventSuggestion"],
    )
    def post(self, request):
        """
        여러 개의 (question, event) 매핑을 받아서 EventSuggestion에 저장
        activity는 Event -> Activity에서 가져와 자동 저장
        """
        data = request.data  # JSON 배열

        if not isinstance(data, list):
            return Response({"error": "List of mappings required"}, status=400)

        created_suggestions = []
        for item in data:
            try:
                q_id = item.get("question")
                e_id = item.get("event")

                if not q_id or not e_id:
                    continue

                question = QuestionList.objects.filter(id=q_id).first()
                event = Event.objects.filter(id=e_id).select_related("activity").first()

                if not question or not event:
                    continue

                # Event에서 연결된 Activity 이름 가져오기
                activity_name = event.activity.activity_name if event.activity else None

                suggestion, created = EventSuggestion.objects.update_or_create(
                    question=question,
                    event=event,
                    defaults={"activity": activity_name},
                )

                created_suggestions.append({
                    "id": suggestion.id,
                    "question": suggestion.question.id,
                    "event": suggestion.event.id,
                    "activity": suggestion.activity
                })

            except Exception as e:
                print("Error saving EventSuggestion:", e)

        return Response({"saved": created_suggestions}, status=201)
    
class EventSuggestionListView(APIView):    
    @swagger_auto_schema(
        operation_summary="이벤트 추천 조회",
        operation_description="특정 question_id에 연결된 EventSuggestion 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "question_id",
                openapi.IN_QUERY,
                description="조회할 문항 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="EventSuggestion 목록",
                examples={
                    "application/json": {
                        "suggestions": [
                            {
                                "id": 10,
                                "question": 1,
                                "event": 5,
                                "event_name": "사설 프로세스 개선",
                                "activity": "대학신문"
                            },
                            {
                                "id": 11,
                                "question": 1,
                                "event": 7,
                                "event_name": "홈커밍 프로젝트",
                                "activity": "대학신문"
                            }
                        ]
                    }
                }
            ),
            400: "잘못된 요청",
            404: "해당 question_id에 추천 이벤트 없음",
        },
        tags=["EventSuggestion"],
    )
    def get(self, request,question_id):

        suggestions = (
            EventSuggestion.objects
            .filter(question_id=question_id)
            .select_related("event__activity")
        )

        if not suggestions.exists():
            return Response({"error": "No suggestions found"}, status=404)

        results = []
        for s in suggestions:
            results.append({
                "id": s.id,
                "question": s.question.id,
                "event": s.event.id,
                "event_name": s.event.event_name,
                "activity": s.activity, 
            })

        return Response({"suggestions": results}, status=200)