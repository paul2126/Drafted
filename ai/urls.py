from django.urls import path
from . import views
from .views import (
    GenerateEmbeddingsView,
    AnalyzeQuestionView,
    EventSuggestionView,
    ChatSessionView,
    ChatMessageView,
    EventSuggestionListView,

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
                    EventSuggestionView.as_view(),
                    name="event-suggestions",
                ),
                path("suggestions/<int:question_id>/", EventSuggestionListView.as_view(), name="event-suggestions-list"),
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

]
