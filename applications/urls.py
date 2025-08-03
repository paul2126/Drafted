from django.urls import path
from . import views


urlpatterns = [
    path("questions/<int:question_id>/guideline/", QuestionGuidelineView.as_view(), name="question-guideline"),
]
