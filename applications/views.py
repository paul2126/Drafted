from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import Application, QuestionList
from .serializers import ApplicationCreateSerializer, QuestionSerializer, EventRecommendSerializer

# Create your views here.
class ApplicationCreateView(APIView):