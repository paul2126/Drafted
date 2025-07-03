import os
import sys
import json
import django
import environ
from django.test import RequestFactory
from unittest.mock import patch, MagicMock

# ✅ .env 로드 및 Django 셋업
env = environ.Env()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drafted.settings")
django.setup()

# ✅ 실제 함수 임포트
from ai.views import analyze_question

# ✅ RequestFactory 사용
body_data = {
    "application_id": 750587254596,
    "question_id": 1,
    "question": "팀 프로젝트에서 갈등을 해결한 경험을 작성해주세요."
}
factory = RequestFactory()
request = factory.post(
    "/fake-url/",
    data=json.dumps(body_data),
    content_type="application/json"
)

# ✅ Vertex API 호출 부분을 Mock!
with patch("ai.views.gen_model.generate_content") as mock_generate_content:
    mock_response = MagicMock()
    mock_response.text = "Mocked AI response text"
    mock_generate_content.return_value = mock_response

    response = analyze_question(request)

    print("\n=== ✅ 함수 실행 결과 (Mock) ===")
    print(response.content.decode("utf-8"))
