from django.urls import path
from . import views
from views import QuestionGuidelineView,QuestionEditorGuidelineView

urlpatterns = [
    path("questions/<int:question_id>/guideline/", QuestionGuidelineView.as_view(), name="question-guideline"),
    path("questions/<int:question_id>/editor-guideline/", QuestionEditorGuidelineView.as_view(), name="question-editor-guideline"),
]
