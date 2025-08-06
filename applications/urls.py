from django.urls import path
from . import views
from .views import (
    ApplicationCreateView,
    ApplicationListView,
    ApplicationDetailView,
    ApplicationDeleteView,
    QuestionGuidelineView,
    QuestionEventRecommendView,
    QuestionEditorGuidelineView,
)

urlpatterns = [
    # 1.지원서 CRUD
    path("create/", ApplicationCreateView.as_view(), name="application-create"),           # POST: 새 지원서 작성
    path("", ApplicationListView.as_view(), name="application-list"),                     # GET: 지원서 목록 조회
    path("<int:application_id>/", ApplicationDetailView.as_view(), name="application-detail"),  # GET: 특정 지원서 상세 조회
    path("<int:application_id>/delete/", ApplicationDeleteView.as_view(), name="application-delete"), #DELETE: 지원서 삭제
    #2.문항별 AI 가이드라인 & 추천 활동
    path("questions/<int:question_id>/guideline/", QuestionGuidelineView.as_view(), name="question-guideline"),
    path("questions/<int:question_id>/recommend/", QuestionEventRecommendView.as_view(), name="question-event-recommend"), 
    # 3.Editor - 문항별 작성 가이드라인
    path("questions/<int:question_id>/editor-guideline/", QuestionEditorGuidelineView.as_view(), name="question-editor-guideline"),
]
