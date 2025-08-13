from django.urls import path
from . import views

urlpatterns = [
    # Chat URLs
    path("sessions/", views.ChatSessionView.as_view(), name="chat_sessions"),
    path(
        "sessions/<int:session_id>/",
        views.ChatSessionDetailView.as_view(),
        name="chat_session_detail",
    ),
    path(
        "sessions/<int:session_id>/messages/",
        views.ChatMessageView.as_view(),
        name="chat_messages",
    ),
]
