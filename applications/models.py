from django.db import models
from users.models import Profile
from activities.models import Activity

class Application(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.TextField()
    position = models.TextField(null=True, blank=True)
    notice = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    end_date = models.DateField(null=True, blank=True)
    activity_name = models.CharField(max_length=255, help_text="지원서 제목 (지원 활동명)")
        
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
