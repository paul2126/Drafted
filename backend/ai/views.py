from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import AiAnalysis, AiSuggestion
from applications.models import QuestionList
from activities.models import Activity, Event
from openai import OpenAI
import environ
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
env = environ.Env()


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

        client = OpenAI(api_key=env("OPENAI_KEY"))

        for chunk in chunk_text(long_text):
            response = client.embeddings.create(
                input=chunk, model="text-embedding-3-small"
            )
            # store each embedding with its chunk

        response = client.embeddings.create(
            input="Your text string goes here", model="text-embedding-3-small"
        )
        # Mock data for demonstration - replace this with your actual data processing
        ability_list = [
            {
                "id": 1,
                "ability": "문제해결능력",
                "description": "복잡한 상황에서 문제를 파악하고 해결방안을 도출하는 능력",
            },
            {
                "id": 2,
                "ability": "의사소통능력",
                "description": "자신의 의견을 명확히 전달하고 타인의 의견을 경청하는 능력",
            },
            {
                "id": 3,
                "ability": "리더십",
                "description": "팀을 이끌고 목표를 달성하도록 영향력을 행사하는 능력",
            },
        ]

        activity_list = [
            {
                "id": 1,
                "activity": "학생회 프로젝트 리더",
                "fit": 0.85,
                "events_list": [
                    {"id": 1, "event": "팀장 | 리더십 | 팀 목표 설정 및 달성"},
                    {"id": 2, "event": "기획자 | 문제해결 | 행사 기획 및 실행"},
                ],
            },
            {
                "id": 2,
                "activity": "동아리 발표 세미나",
                "fit": 0.75,
                "events_list": [
                    {"id": 3, "event": "발표자 | 의사소통 | 기술 세미나 진행"}
                ],
            },
        ]

        # Prepare the response
        response_data = {"ability_list": ability_list, "activity_list": activity_list}

        return JsonResponse(response_data, status=200)

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
