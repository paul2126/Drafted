from django.db import models
from applications.models import QuestionList


class AiSuggestion(models.Model):
    question = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    activity = models.TextField()
    useful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_suggestion"


class AiAnalysis(models.Model):
    question = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    ability = models.TextField()
    useful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_analysis"
