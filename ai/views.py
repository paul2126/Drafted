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


tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
env = environ.Env()


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

        #########################################################################################
        # Parse the response
        parsed_result_json = parse_ai_suggestion_to_json(response.data)
        print(parsed_result_json)
        #########################################################################################
        # Mock data for demonstration - replace this with your actual data processing
        # ability_list = [
        #     {
        #         "id": 1,
        #         "ability": "문제해결능력",
        #         "description": "복잡한 상황에서 문제를 파악하고 해결방안을 도출하는 능력",
        #     },
        #     {
        #         "id": 2,
        #         "ability": "의사소통능력",
        #         "description": "자신의 의견을 명확히 전달하고 타인의 의견을 경청하는 능력",
        #     },
        #     {
        #         "id": 3,
        #         "ability": "리더십",
        #         "description": "팀을 이끌고 목표를 달성하도록 영향력을 행사하는 능력",
        #     },
        # ]

        # activity_list = [
        #     {
        #         "id": 1,
        #         "activity": "학생회 프로젝트 리더",
        #         "fit": 0.85,
        #         "events_list": [
        #             {"id": 1, "event": "팀장 | 리더십 | 팀 목표 설정 및 달성"},
        #             {"id": 2, "event": "기획자 | 문제해결 | 행사 기획 및 실행"},
        #         ],
        #     },
        #     {
        #         "id": 2,
        #         "activity": "동아리 발표 세미나",
        #         "fit": 0.75,
        #         "events_list": [
        #             {"id": 3, "event": "발표자 | 의사소통 | 기술 세미나 진행"}
        #         ],
        #     },
        # ]

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





##############################application views 를 위한 임시 목업 결과들..###################
#for applications 2-1 
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
            )
        }

        return JsonResponse(response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

#for 2-2 . get: 문항별 AI 추천 활동 5개

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

        #Mock response - replace with actual AI call
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
                    "comment": "서비스 개발 관심과 실행력을 보여주는 이벤트입니다."
                },
                {
                    "activity_name": "멋쟁이사자처럼",
                    "event_name": "해커톤 프로젝트",
                    "situation": "팀 해커톤에서 웹서비스 개발",
                    "task": "백엔드 개발 담당",
                    "action": "API 설계 및 구현",
                    "result": "최우수상 수상",
                    "contribution": 85.0,
                    "comment": "실무 개발 경험과 협업 능력을 강조할 수 있습니다."
                },
                {
                    "activity_name": "대학신문 활동",
                    "event_name": "사설 프로세스 개선",
                    "situation": "편집장으로서 프로세스 문제 인식",
                    "task": "문제 진단 및 개선안 설계",
                    "action": "새로운 제작 프로세스 도입",
                    "result": "오류율 50% 감소",
                    "contribution": 80.0,
                    "comment": "문제 해결 과정이 잘 드러납니다."
                }
            ],
            "tip": "이런 활동들을 중심으로 문항을 구성하면 문제 해결력과 실행력이 더 명확하게 드러납니다."
        }

        return JsonResponse(ai_result, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    

#for 3-1. get: 문항별 작성 가이드라인 
@csrf_exempt
def editor_guideline(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id", 0)
        #Mock response - replace with actual AI call
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
            )
        }

        return JsonResponse(dummy_response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
###############################################################