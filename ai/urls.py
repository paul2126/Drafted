from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.analyze_question, name="analyze_question"),
    ##########지원서 뷰스를 위한 임시##########
    path("question-guideline/", views.generate_question_guideline, name="generate_question_guideline"),
]
