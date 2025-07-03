from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.analyze_question, name="analyze_question"),
]
