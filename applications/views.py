from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from users.models import Profile
from .models import Application, QuestionList
from .serializers import ApplicationCreateSerializer,  EventRecommendSerializer,QuestionGuideSerializer , ApplicationListSerializer,ApplicationDetailQuestionSerializer

from django.conf import settings
import requests

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


user_id_header = openapi.Parameter(
    "X-USER-ID", openapi.IN_HEADER, description="Supabase User ID", type=openapi.TYPE_STRING, required=True
)
#1. 지원서 작성 및 목록 조회
#1-1. post: 새 지원서 작성
class ApplicationCreateView(APIView):
  @swagger_auto_schema(
      operation_summary="지원서 생성",
      operation_description="새로운 지원서를 생성하고 생성된 지원서 ID를 반환합니다.",
      manual_parameters=[user_id_header],
      request_body=ApplicationCreateSerializer,
      responses={201: openapi.Response(description="지원서 ID", examples={"application/json": {"id": 1}})},
  )
  def post(self, request):
    #for supabase jwt
    user_id = request.headers.get("X-USER-ID") or request.data.get("user_id")
    profile = get_object_or_404(Profile, user_id=user_id)

    serializer = ApplicationCreateSerializer(data=request.data)
    if serializer.is_valid():
      # 지원서 인스턴스 생성
      app = Application.objects.create(
        user=profile,
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
      return Response({"id": app.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#1-2. get: 지원서 목록 조회
class ApplicationListView(APIView):
  @swagger_auto_schema(
      operation_summary="지원서 목록 조회",
      operation_description="로그인한 사용자의 모든 지원서를 조회합니다.(최신순말고 마감순으로 하면 좋을듯)",
      manual_parameters=[user_id_header],
      responses={200: openapi.Response(description="지원서 목록", schema=ApplicationListSerializer(many=True))},
  )
  def get(self, request):
    #for supabase jwt
    user_id = request.headers.get("X-USER-ID") or request.data.get("user_id")
    profile = get_object_or_404(Profile, user_id=user_id)

    applications = Application.objects.filter(user=profile) #.order_by("-created_at")
    serializer = ApplicationListSerializer(applications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#1-3. get : 특정 지원서 detail 내용 조회
class ApplicationDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="지원서 상세 조회",
        operation_description="특정 지원서의 모든 문항과 작성 내용을 조회합니다.",
        manual_parameters=[user_id_header],
        responses={200: ApplicationDetailQuestionSerializer(many=True)},
    )
    def get(self, request, application_id):
      #for supabase jwt
      user_id = request.headers.get("X-USER-ID") or request.data.get("user_id")
      profile = get_object_or_404(Profile, user_id=user_id)

      app = get_object_or_404(Application, id=application_id, user=profile)
      questions = QuestionList.objects.filter(application=app).order_by("id")
      serializer = ApplicationDetailQuestionSerializer(questions, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

#1-4. delete: 지원서 삭제
class ApplicationDeleteView(APIView):
    @swagger_auto_schema(
        operation_summary="지원서 삭제",
        operation_description="지원서 ID를 Path Parameter로 받아 해당 지원서를 삭제합니다.",
        responses={200: openapi.Response("삭제 성공", examples={"application/json": {"message": "지원서가 성공적으로 삭제되었습니다."}})},
    )
    def delete(self, request, application_id):
        #for supabase jwt
        user_id = request.headers.get("X-USER-ID") or request.data.get("user_id")
        profile = get_object_or_404(Profile, user_id=user_id)

        app = get_object_or_404(Application, id=application_id, user=profile)
        app.delete()
        return Response({"message": "지원서가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)  

#2. 문항별 활동 가이드라인 + AI 추천 활동 5개
#2-1. get: 문항별 활동 가이드라인 
class QuestionGuidelineView(APIView):
    @swagger_auto_schema(
        operation_summary="문항별 활동 가이드라인",
        operation_description="특정 문항에 대한 AI 활동 가이드라인을 반환합니다.",
        responses={200: QuestionGuideSerializer()},
    )
    def get(self, request, question_id):
        question = get_object_or_404(QuestionList, id=question_id)

        payload = {"question_id": question.id, "question": question.question}

        try:
            ai_response = requests.post(settings.AI_GUIDELINE_URL, json=payload, timeout=10)

            if ai_response.status_code != 200:
                return Response({"error": "AI 서버 오류"}, status=status.HTTP_502_BAD_GATEWAY)

            ai_data = ai_response.json()
            serializer = QuestionGuideSerializer(ai_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"AI 서버 요청 실패: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


#2-2 . get: 문항별 AI 추천 활동 5개
class QuestionEventRecommendView(APIView):
  @swagger_auto_schema(
      operation_summary="문항별 AI 추천 활동",
      operation_description="특정 문항과 관련된 AI 추천 활동 5개를 반환합니다.",
      responses={200: EventRecommendSerializer()},
  )
  def get(self, request, question_id):
    question = get_object_or_404(QuestionList, id=question_id)
    payload = {
        "question_id": question.id,
        "question": question.question
    }
    try:
        ai_response = requests.post(settings.AI_RECOMMEND_URL, json=payload, timeout=10)

        if ai_response.status_code != 200:
            return Response({"error": "AI 서버 오류"}, status=status.HTTP_502_BAD_GATEWAY)

        ai_data = ai_response.json()
        ### 짜둔 지원서 구조화하기 LLM 프롬프트 쓸 때 => 프론트 요구 형태로 변환
        eventlist = [
            {
                "id": idx + 1,
                "title": e["event_name"],
                "activity": e["activity_name"],
                "comment": e["comment"],
                "is_recommended": (e.get("contribution", 0) >= 70.0)
            }
            for idx, e in enumerate(ai_data.get("suggested_events", [])[:5])
        ]

        response_data = {
            "question_id": question.id,
            "suggestion": ai_data.get("analysis", "AI 분석 결과 없음"),
            "eventlist": eventlist
        }

        serializer = EventRecommendSerializer(data=response_data)
        if serializer.is_valid():
          return Response(serializer.data, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
      return Response({"error": f"AI 서버 오류: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    

#3. editor 지원서 작성 및 첨삭
#3-1. get: 문항별 작성 가이드라인 
class QuestionEditorGuidelineView(APIView):
    @swagger_auto_schema(
        operation_summary="문항별 AI 추천 활동",
        operation_description="특정 문항과 관련된 AI 추천 활동 5개를 반환합니다.",
        responses={200: EventRecommendSerializer()},
    )
    def get(self, request, question_id):
        question = get_object_or_404(QuestionList, id=question_id)

        payload = {"question_id": question.id, "question": question.question}

        try:
            ai_response = requests.post(settings.AI_EDITOR_GUIDELINE_URL, json=payload, timeout=10)
            if ai_response.status_code != 200:
                return Response({"error": "AI 서버 오류"}, status=status.HTTP_502_BAD_GATEWAY)

            ai_data = ai_response.json()
            return Response(ai_data, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"AI 서버 요청 실패: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)