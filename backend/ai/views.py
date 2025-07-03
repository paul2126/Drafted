from django.shortcuts import render

# Create your views here.
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

from vertexai.preview.generative_models import GenerativeModel
from supabase import create_client

from .models import AiAnalysis, AiSuggestion
from applications.models import QuestionList
from activities.models import Activity, Event  # 너의 앱 이름에 맞게 수정

import vertexai
import environ
env = environ.Env()

gen_model = GenerativeModel("gemini-pro")
supabase_url  = env("DB_URL")
supabase_key = env("DB_PRIVATE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL or Key is not set in the environment variables.")
else:
  supabase=create_client(supabase_url , supabase_key)
print(env("PROJECT_ID"))
vertexai.init(
    project=env("PROJECT_ID"),
    location=env("REGION")  
)

@csrf_exempt
def analyze_question(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 지원됩니다.'}, status=400)

    body = json.loads(request.body)
    application_id = body.get('application_id')
    question_id = body.get('question_id')
    question = body.get('question')

    if not (application_id and question_id and question):
        return JsonResponse({'error': '필수 필드 누락'}, status=400)

    # 1 역량 분석
    prompt = f"""
            너는 채용 전문가 AI야.

            너의 임무는 아래 자기소개서 문항(question)을 보고  
            이 문항에서 평가하려는 핵심 역량(ability)을 최대 3~5개 정도 도출하는 것이야.

            각 역량은 다음과 같이 포함되어야 해:
            - ability: 역량 이름 (간결하고 대표적인 한 단어 또는 짧은 문구)
            - description: 이 역량이 어떤 의미인지 설명 (1~2문장)

            반드시 아래 JSON 형식으로만 출력해:
            [
              {{
                "ability": "문제해결능력",
                "description": "복잡한 상황에서 문제를 정의하고 해결 방안을 찾아내는 능력"
              }},
              {{
                "ability": "의사소통능력",
                "description": "팀원 및 이해관계자와 효과적으로 정보를 교환하고 협업하는 능력"
              }}
            ]

            문항:
            \"\"\"
            {question}
            \"\"\"
    """

    gen_model = GenerativeModel("gemini-pro")
    response = gen_model.generate_content(prompt)
    ability_list = json.loads(response.text)

    #  질문 임베딩 생성
    embed_model = GenerativeModel("gemini-embedding-001")
    embedding_response = embed_model.get_embeddings([question])
    question_embedding = embedding_response.embeddings[0].values

    #  Supabase로 활동 유사도 검색

    embedding_str = ','.join([str(v) for v in question_embedding])
    sql_query = f"""
        SELECT
            id,
            user_id,
            content,
            1 - (embedding <=> ARRAY[{embedding_str}]) AS similarity
        FROM activity_embedding
        ORDER BY embedding <=> ARRAY[{embedding_str}]
        LIMIT 5;
    """
    result = supabase.postgrest.query(sql_query).execute()
    embedding_rows = result.data

    # DB 저장
    question_obj = QuestionList.objects.get(id=question_id)

    activity_list = []
    for row in embedding_rows:
        embedding_id = row['id']
        user_id = row['user_id']
        content = row['content']
        similarity = row['similarity']

        # Activity 연결
        activity_qs = Activity.objects.filter(user_id=user_id)
        events_list = []
        if activity_qs.exists():
            activity = activity_qs.first()
            events = Event.objects.filter(activity_id=activity.id)
            events_list = [
                {
                    "id": e.id,
                    "event": f"{e.role} | {e.ability} | {e.my_action}"
                }
                for e in events
            ]

        # AiSuggestion 저장
        AiSuggestion.objects.create(
            question_id=question_obj,
            activity=content,
            useful=False
        )

        activity_list.append({
            "id": embedding_id,
            "activity": content,
            "fit": float(similarity),
            "events_list": events_list
        })

    #### AiAnalysis 저장
    for ability in ability_list:
        AiAnalysis.objects.create(
            question_id=question_obj,
            ability=ability['ability'],
            useful=False
        )

    #### 반환
    question_response = {
        "ability_list": [
            {
                "id": idx + 1,
                "ability": ab['ability'],
                "description": ab['description']
            }
            for idx, ab in enumerate(ability_list)
        ],
        "activity_list": activity_list
    }


    return JsonResponse({"question_response": question_response}, status=200)



