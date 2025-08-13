from django.urls import path
from . import views
from .views import (
    GenerateEmbeddingsView,
    AnalyzeQuestionView,
    EventSuggestionsView,
    ChatSessionView,
    ChatMessageView,
    QuestionGuidelineAIView,
    QuestionEventRecommendAIView,
    QuestionEditorGuidelineAIView,
)
from django.urls import include

urlpatterns = [
    # 1. Embedding Management
    path(
        "embeddings/",
        GenerateEmbeddingsView.as_view(),
        name="generate-embeddings",
    ),
    # 2. Question Analysis & Matching
    path(
        "questions/",
        include(
            [
                path(
                    "analyze/", AnalyzeQuestionView.as_view(), name="analyze-question"
                ),
                path(
                    "suggestions/",
                    EventSuggestionsView.as_view(),
                    name="event-suggestions",
                ),
            ]
        ),
    ),
    # 3. Personal Statement Chat
    # path(
    #     "chat/",
    #     include(
    #         [
    #             path("sessions/", ChatSessionView.as_view(), name="chat-sessions"),
    #             path(
    #                 "sessions/<uuid:session_id>/",
    #                 ChatDetailView.as_view(),
    #                 name="chat-detail",
    #             ),
    #             path(
    #                 "sessions/<uuid:session_id>/messages/",
    #                 ChatMessageView.as_view(),
    #                 name="chat-messages",
    #             ),
    #             path(
    #                 "generate/",
    #                 GenerateStatementView.as_view(),
    #                 name="generate-statement",
    #             ),
    #         ]
    #     ),
    # ),
    # path("analyze/", views.analyze_question, name="analyze-question"),
    # application ai
    path(
        "application/<int:question_id>/guideline/",
        QuestionGuidelineAIView.as_view(),
        name="question-guideline",
    ),

    # 문항별 AI 추천 활동
    path(
        "application/<int:question_id>/recommend/",
        QuestionEventRecommendAIView.as_view(),
        name="question-event-recommend",
    ),

    # 문항별 에디터용 가이드라인
    path(
        "application/<int:question_id>/editor-guideline/",
        QuestionEditorGuidelineAIView.as_view(),
        name="question-editor-guideline",
    ),
]
