from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import Application, QuestionList
from .serializers import ApplicationCreateSerializer, QuestionSerializer, EventRecommendSerializer,QuestionGuideSerializer

from django.conf import settings
import requests


#1. 지원서 작성 및 목록 조회
#1-1. post: 새 지원서 작성
class ApplicationCreateView(APIView):
  def post(self, request):
    serializer = ApplicationCreateSerializer(data=request.data)
    if serializer.is_valid():
      # 지원서 인스턴스 생성
      app = Application.objects.create(
        user=request.user.profile,
        category=serializer.validated_data['category'],
        position=serializer.validated_data.get('position'),
        notice=serializer.validated_data.get('notice')
      )
      # 질문 리스트 생성
      for q in serializer.validated_data['questions']:
        QuestionList.objects.create(
          application=app,
          question=q['content'],
          max_length=q['max_characters'],
          question_explanation=q.get('question_explanation', '')
        )
      return Response({"message": "Application created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#1-2. get: 지원서 목록 조회
class ApplicationListView(APIView):
  def get(self, request):
    applications = Application.objects.filter(user=request.user.profile) #.order_by("-created_at")
    serializer = ApplicationCreateSerializer(applications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  

#2. 문항별 활동 가이드라인 + AI 추천 활동 5개
#2-1. get: 문항별 활동 가이드라인 
class QuestionGuidelineView(APIView):
    def get(self, request, question_id):
        question = get_object_or_404(QuestionList, id=question_id)
        ai_url = getattr(settings, "AI_GUIDELINE_URL", "http://localhost:8000/ai/question-guideline/")

        payload = {"question_id": question.id, "question": question.question}

        try:
            ai_response = requests.post(ai_url, json=payload, timeout=10)

            if ai_response.status_code != 200:
                return Response({"error": "AI 서버 오류"}, status=status.HTTP_502_BAD_GATEWAY)

            ai_data = ai_response.json()
            serializer = QuestionGuideSerializer(ai_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"AI 서버 요청 실패: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


