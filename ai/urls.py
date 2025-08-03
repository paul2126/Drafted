from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.analyze_question, name="analyze_question"),
    ##########지원서 뷰스를 위한 임시##########
    path("question-guideline/", views.generate_question_guideline, name="generate_question_guideline"),
    path("recommend/", views.recommend_events, name="recommend_events"),
    path("editor-guideline/", views.generate_editor_guideline, name="generate_editor_guideline"),
]
