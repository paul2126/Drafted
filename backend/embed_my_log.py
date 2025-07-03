from openai import OpenAI
import environ
import tiktoken
from supabase import create_client, Client
from pathlib import Path
import os
from datetime import datetime

tokenizer = tiktoken.get_encoding("cl100k_base")  # For embedding-3 models
env = environ.Env()

environ.Env.read_env(env_file=os.path.join(os.path.dirname(__file__), ".env"))
# print(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = env("DB_URL")
SUPABASE_KEY = env("DB_KEY")

client = OpenAI(api_key=env("OPENAI_KEY"))
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

text = """
[
  {
    "id": 1,
    "name": "대학신문",
    "status": false,
    "description": "2022년 3월부터 2024년 11월까지 취재부 평기자, 차장, 편집장, 뉴미디어부 콘텐츠 기자로 활동함",
    "favorite": true,
    "position": "편집장",
    "startdate": "2023-06-20",
    "enddate": "2023-09-25",
    "related_docs": [],
    "event": [
      {
        "id": "evt-001",
        "name": "사설 프로세스 개선",
        "startdate": "2023-07-12",
        "enddate": "2023-08-29",
        "role": "현황 진단 및 문제 정의",
        "category": ["문제해결능력", "조직관리역량", "분석력"],
        "ability": {},
        "data": {
          "background": "사설 제작 주기가 길고 오류가 잦다는 문제를 해결하기 위해 현행 프로세스를 파악하고 병목 구간을 찾음.",
          "my_action": "기존 부서들의 사설 작성 프로세스를 추적하고 업무 충돌 및 리소스가 과하게 투입되는 지점 확인 및 개선안 도출\n이전 기수 선배들 및 대학신문사에 오래 머문 간사단과 소통함으로써 제시한 해결책이 적절한 방향성인지 점검\n자문위원 교수 및 행정실에게 사전 문건을 공유하고 두 차례의 전사 내부 회의를 토대로 프로세스 개선에 합의 도출",
          "result": "사설 퇴고가 완료되는 시점이 주말에서 금요일로 1일 단축, 데스크 부담 경감으로 업무 효율성 상승, 기자단 및 자문위원 만족도 상승.",
          "reflection": "기존의 방식을 무조건 지키려고 하기보다 효율적으로 대응할 수 있는 방법을 적극적으로 찾아야 한다는 점을 배움."
        }
      },
      {
        "id": "evt-002",
        "name": "전 기수 대상 홈커밍 프로젝트 기획",
        "startdate": "2023-07-22",
        "enddate": "2023-11-15",
        "role": "전 기수 대상 홈커밍 프로젝트 기획",
        "category": ["기획력", "추진 및 진행력", "관계관리역량"],
        "ability": {},
        "data": {
          "background": "코로나19 이후로 선후배 간 단절이 심화되고, 대학신문 활동의 지속성과 유대감이 약화되고 있다는 문제의식을 바탕으로, 졸업한 선배들과의 재접점을 마련하고자 함.",
          "my_action": "전 기수 명단을 확보하고 이메일·SNS를 통해 연락망을 복원함. 행사 목적과 참여방식을 정리한 안내문과 참여 설문지를 발송하였으며, 학교 공간 대관, 프로그램 기획(토크콘서트, 전시, 네트워킹 세션)을 총괄 기획함.",
          "result": "총 12개 기수, 60여 명의 졸업생이 참여하여, 신입기수 10명과의 교류가 성사됨. 이후 멘토링·취재 협조 등 협업 기반을 구축하게 되었고, 내부 구성원 만족도 4.8/5로 기록.",
          "reflection": "커뮤니티가 단절될 경우 구성원 이탈로 이어질 수 있음을 체감했고, 기획 초기부터 '공감 가는 명분'과 '참여 진입장벽 최소화'가 성공의 핵심임을 배움."
        }
      }
    ]
  },
  {
    "id": 2,
    "name": "SNEW 학회",
    "status": false,
    "description": "뉴미디어 마케팅 학회에서 학회원으로 활동하며 다양한 스타트업과 마케팅 실무 프로젝트 경험",
    "favorite": false,
    "position": "학회원",
    "startdate": "2023-03-12",
    "enddate": "2023-12-30",
    "related_docs": [],
    "event": [
      {
        "id": "evt-003",
        "name": "S2 엔터테인먼트 프로젝트 결과보고",
        "startdate": "2023-06-01",
        "enddate": "2023-06-17",
        "role": "팀장",
        "category": ["콘텐츠 기획력", "인사이트 도출", "디지털 채널 운영 역량"],
        "ability": {},
        "data": {
          "background": "S2엔터테인먼트는 신인 아티스트의 브랜드 메시지인 'BORN TO BE XX'를 중심으로 숏폼 콘텐츠 챌린지와 세계관 기반 스토리텔링 전략을 수립하였으며, 컴백 초기 단계의 팬 유입과 화제성 증대를 위한 온고잉 성과 보고가 필요해짐.",
          "my_action": "틱톡, 유튜브 쇼츠, 인스타 릴스를 중심으로 각 플랫폼별 콘텐츠 퍼포먼스를 모니터링하고, 해시태그 사용량, 참여율, 팬 피드백을 기반으로 주요 지표를 정리함.\n챌린지 참여율이 높았던 ‘손가락 안무’, ‘립싱크 리액션’ 콘텐츠 유형의 확장 방향을 제안하였으며, 세계관 관련 추측 콘텐츠에 대한 팬 커뮤니티 반응을 수집해 서브 콘텐츠 방향성을 구체화함.",
          "result": "틱톡 해시태그 조회수 11,000,000회 돌파, 챌린지 참여 영상 약 3,800건 생성.\n팬 커뮤니티 내 세계관 해석 콘텐츠 약 250건 파생되었으며, 2차 창작 기반 팬 유입 및 전환율이 증가함.\n해외 Z세대 대상 신규 팔로워 비율이 28%로 상승.",
          "reflection": "틱톡을 중심으로 한 숏폼 콘텐츠는 팬과 일반 대중 모두의 자발적 확산을 유도하는 데 효과적임을 확인함. 세계관의 빈칸을 남긴 콘텐츠 전략은 팬의 몰입을 높이며, 참여 기반 브랜딩에 긍정적임을 체감함."
        }
      },
      {
        "id": "evt-004",
        "name": "빅플래닛메이드엔터 결과보고",
        "startdate": "2023-10-22",
        "enddate": "2023-11-24",
        "role": "개인 프로젝트로 전체 전담",
        "category": ["캠페인 설계 능력", "기획력", "브랜드 감수성 고려"],
        "ability": {},
        "data": {
          "background": "소유의 신곡 ‘Aloha’ 발매를 앞두고, ‘썸머퀸’ 이미지 강화와 2010년대 향수 마케팅을 접목한 다양한 콘텐츠와 채널 연계를 통해 팬과 대중의 초기 반응을 유도하고자 함.",
          "my_action": "뮤직비디오 콘셉트, 다이어트 댄스 챌린지, 팝업스토어 기획 등 온·오프라인 연계 프로모션을 설계하고, 콘텐츠별 퍼포먼스를 중간 점검함.\n운동 유튜버와의 챌린지 협업, 씨스타와 연계한 추억 안무 챌린지 제안, 리무진서비스 등 유튜브 콘텐츠 타깃 출연 전략을 구성.",
          "result": "틱톡 기준 ‘#소유알로하’ 챌린지 영상 2,100건 이상 업로드. ‘짬에서 나오는 바이브’ 콘셉트에 대한 팬 공감 댓글 다수 확보.\n팝업스토어 인스타그램 사전 팔로워 3,000명 이상, 여름휴가지 테마 굿즈 사전 관심도 증가.",
          "reflection": "과거 정체성을 긍정적으로 계승하면서도 새로운 콘셉트를 제시할 때, 콘텐츠 기획 전반에 ‘공감 가능한 맥락’과 ‘가벼운 진입장벽’이 매우 중요함을 실감함."
        }
      }
    ]
  }
]
"""

# test code
# now = datetime.now().isoformat()  # Convert to ISO format string
# response = (
#     supabase.table("activity_embedding")
#     .insert(
#         {
#             "user_id": "ab3312ab-975e-4421-bae4-ca1cc5bbadf4",
#             "content": text,
#             "embedding": client.embeddings.create(
#                 input="hello", model="text-embedding-3-small"
#             )
#             .data[0]
#             .embedding,
#             "favorite": False,
#             "created_at": now,  # Use ISO format string
#             "updated_at": now,  # Use ISO format string
#         }
#     )
#     .execute()
# )


def chunk_text(text, max_tokens=8000):
    tokens = tokenizer.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + max_tokens]
        chunks.append(tokenizer.decode(chunk))
        i += max_tokens
    return chunks


for chunk in chunk_text(text):
    embedding_response = client.embeddings.create(
        input=chunk, model="text-embedding-3-small"
    )
    # store each embedding with its chunk

    response = (
        supabase.table("activity_embedding")
        .insert(
            {
                "user_id": "ab3312ab-975e-4421-bae4-ca1cc5bbadf4",
                "content": chunk,
                "embedding": embedding_response.data[0].embedding,
                "favorite": False,
                "created_at": now,  # Use ISO format string
                "updated_at": now,  # Use ISO format string
            }
        )
        .execute()
    )
