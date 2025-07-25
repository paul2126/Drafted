from django.db import models
from users.models import Profile


class Application(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.TextField()
    position = models.TextField(null=True, blank=True)
    notice = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "application"


class QuestionList(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    question = models.TextField()
    max_length = models.IntegerField()
    question_explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question_list"
