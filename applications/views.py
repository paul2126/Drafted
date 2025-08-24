from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from users.models import Profile
from .models import Application, QuestionList
from .serializers import ApplicationCreateSerializer,  EventRecommendSerializer,QuestionGuideSerializer , ApplicationListSerializer,ApplicationDetailQuestionSerializer
from ai.utils import recommend_events

from django.conf import settings
import requests

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.supabase_utils import get_supabase_client, get_user_id_from_token
from ai.views import generate_question_guideline,generate_editor_guideline

import json
from django.http import JsonResponse
#1. 지원서 작성 및 목록 조회
#1-1. post: 새 지원서 작성
class ApplicationCreateView(APIView):
  @swagger_auto_schema(
      operation_summary="지원서 생성",
      operation_description="새로운 지원서를 생성하고 생성된 지원서 ID를 반환합니다.",
      request_body=ApplicationCreateSerializer,
      responses={201: openapi.Response(description="지원서 ID", examples={"application/json": {"id": 1}})},
  )
  def post(self, request):
    #for supabase jwt
    supabase = get_supabase_client(request)
    user_id = get_user_id_from_token(request)
    profile = get_object_or_404(Profile, user_id=user_id)
    print(request.data)
    serializer = ApplicationCreateSerializer(data=request.data)
    if serializer.is_valid():
      # 지원서 인스턴스 생성
      app = Application.objects.create(
        user=profile,
        activity_name=serializer.validated_data.get('activity_name'),
        end_date=serializer.validated_data.get('end_date'),
        category=serializer.validated_data['category'],
        position=serializer.validated_data.get('position'),
        notice=serializer.validated_data.get('notice')
      )
      # 질문 리스트 생성
      for q in serializer.validated_data['questions']:
        QuestionList.objects.create(
          application=app,
          question=q['question'],
          max_length=q['max_length'],
          question_explanation=q.get('question_explanation', '')
        )
      return Response({"id": app.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#1-2. get: 지원서 목록 조회
class ApplicationListView(APIView):
  @swagger_auto_schema(
      operation_summary="지원서 목록 조회",
      operation_description="로그인한 사용자의 모든 지원서를 조회합니다.(최신순말고 마감순으로 하면 좋을듯)",
      responses={200: openapi.Response(description="지원서 목록", schema=ApplicationListSerializer(many=True))},
  )
  def get(self, request):
    #for supabase jwt
    supabase = get_supabase_client(request)
    user_id = get_user_id_from_token(request)
    profile = get_object_or_404(Profile, user_id=user_id)

    applications = Application.objects.filter(user=profile) #.order_by("-created_at")
    serializer = ApplicationListSerializer(applications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#1-3. get : 특정 지원서 detail 내용 조회
class ApplicationDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="지원서 상세 조회",
        operation_description="특정 지원서의 모든 문항과 작성 내용을 조회합니다.",
        responses={200: ApplicationDetailQuestionSerializer(many=True)},
    )
    def get(self, request, application_id):
      #for supabase jwt
      supabase = get_supabase_client(request)
      user_id = get_user_id_from_token(request)
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
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)
        profile = get_object_or_404(Profile, user_id=user_id)

        app = get_object_or_404(Application, id=application_id, user=profile)
        app.delete()
        return Response({"message": "지원서가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)  

#1-5 .put: 지원서 수정 
class ApplicationUpdateView(APIView):
    @swagger_auto_schema(
        operation_summary="지원서 수정",
        operation_description=(
            "지원서 ID를 Path Parameter로 받아 해당 지원서를 수정합니다.\n\n"
            "기존 질문(QuestionList)은 모두 삭제 후 새로 전달된 questions로 대체됩니다."
        ),
        request_body=ApplicationCreateSerializer,
        responses={
            200: openapi.Response(
                description="지원서 수정 성공",
                examples={
                    "application/json": {
                        "id": 3,
                        "message": "지원서가 수정되었습니다."
                    }
                },
            ),
            400: openapi.Response(description="요청 데이터 오류"),
            404: openapi.Response(description="지원서 또는 사용자 없음"),
        },
    )
    def put(self, request, application_id):

        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)
        profile = get_object_or_404(Profile, user_id=user_id)
        app = get_object_or_404(Application, id=application_id, user=profile)

        serializer = ApplicationCreateSerializer(data=request.data)
        if serializer.is_valid():
            app.category = serializer.validated_data['category']
            app.end_date = serializer.validated_data['endDate']
            app.position = serializer.validated_data.get('position', app.position)
            app.notice = serializer.validated_data.get('notice', app.notice)
            app.activity_name = serializer.validated_data.get('activity', app.activity_name)
            app.user = profile 
            app.save()

            QuestionList.objects.filter(application=app).delete()
            for q in serializer.validated_data['questions']:
                QuestionList.objects.create(
                    application=app,
                    question=q['content'],
                    max_length=q['max_characters'],
                    question_explanation=q.get('question_explanation', '')
                )

            return Response({"id": app.id, "message": "지원서가 수정되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#2. 문항별 활동 가이드라인 + AI 추천 활동 5개
#2-1. get: 문항별 활동 가이드라인 
class QuestionGuidelineView(APIView):
    @swagger_auto_schema(
        operation_summary="문항별 활동 가이드라인",
        operation_description="특정 문항에 대한 AI 활동 가이드라인을 반환합니다.",
        responses={200: QuestionGuideSerializer()},
    )
 
    def get(self, request, question_id:int):
        question = get_object_or_404(QuestionList, id=question_id)
        #ai_url = settings.AI_GUIDELINE_URL.format(question_id=question.id)

        try:
        
            ai_result = generate_question_guideline( question.question, question.id)
            print(type(ai_result), ai_result)
            if isinstance(ai_result, JsonResponse):
                ai_data = json.loads(ai_result.content)
            else:
                ai_data = ai_result
            print(type(ai_data), ai_data )

            serializer = QuestionGuideSerializer(data=ai_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=200)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"AI 서버 요청 실패: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


#2-2 . get: 문항별 AI 추천 활동 5개
class QuestionEventRecommendView(APIView):
  @swagger_auto_schema(
      operation_summary="문항별 AI 추천 활동",
      operation_description="특정 문항과 관련된 AI 추천 활동 5개를 반환합니다.",
      responses={200: EventRecommendSerializer()},
  )
  def get(self, request, question_id: int):
    question = get_object_or_404(QuestionList, id=question_id)
    payload = {
        "question_id": question.id,
        "question": question.question
    }
    
    try:
        ai_response = recommend_events(question_id, request)

        print("🔍 [DEBUG] AI 추천 활동 응답 타입:", type(ai_response))
        if ai_response.status_code != 200:
            return Response({"error": "AI 응답 오류"}, status=status.HTTP_502_BAD_GATEWAY)
        elif isinstance(ai_response, JsonResponse):
            ai_data = json.loads(ai_response.content)
        elif isinstance(ai_response, Response):
            ai_data = ai_response.data
        else:
            ai_data = ai_response
        print("🔍 [DEBUG] ai_data type:", type(ai_data), ai_data)
        eventlist = [
            {
                "id": e["event_id"],
                "title": e["event_name"],
                "activity": e["activity_name"],
                "comment": e["comment"],
                "is_recommended": (e.get("similarity", 0) >= 0.35)
            }
            for idx, e in enumerate(ai_data.get("suggested_events", [])[:5])
        ]

        response_data = {
            "question_id": question.id,
            #"suggestion": ai_data.get("analysis", "AI 분석 결과 없음"),
            "eventlist": eventlist
        }
        print("🔍 [DEBUG] AI 추천 활동 데이터:", response_data)

        serializer = EventRecommendSerializer(data=response_data)
        if serializer.is_valid():
          return Response(serializer.data, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
      return Response({"error": f"AI 서버 오류: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    

#3. editor 지원서 작성 및 첨삭
#3-1. get: 문항별 작성 가이드라인 
class QuestionEditorGuidelineView(APIView):
    @swagger_auto_schema(
        operation_summary="문항별 작성 가이드라인",
        operation_description="특정 문항에 대한 작성 가이드라인을 반환합니다.",
        responses={200: openapi.Response("작성 가이드라인", examples={"application/json": {"question_id": 1, "content": "### 작성 팁..."}})},
    )
    def get(self, request, question_id:int):
        question = get_object_or_404(QuestionList, id=question_id)

        try:
        
            ai_result = generate_editor_guideline( question.question, question.id)
            print(type(ai_result), ai_result)
            if isinstance(ai_result, JsonResponse):
                ai_data = json.loads(ai_result.content)
            else:
                ai_data = ai_result
            print(type(ai_data), ai_data )

            serializer = QuestionGuideSerializer(data=ai_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=200)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"AI 서버 요청 실패: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
