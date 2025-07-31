from django.db import models
from pgvector.django import VectorField
from django.contrib.postgres.fields import ArrayField

# from django.contrib.postgres.fields import ArrayField  # postgress specific
from users.models import Profile


class Activity(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False, help_text="즐겨찾기 여부")
    activity_name = models.TextField(help_text="활동 제목")
    category = models.TextField(null=True, blank=True, help_text="활동 카테고리")
    position = models.TextField(null=True, blank=True, help_text="활동 역할 및 직책")
    file_list = ArrayField(
        models.TextField(), null=True, blank=True, help_text="첨부파일 목록"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True, blank=True, help_text="활동 시작일")
    end_date = models.DateTimeField(null=True, blank=True, help_text="활동 종료일")
    last_visit = models.DateTimeField(auto_now=True, help_text="마지막 방문일")
    description = models.TextField(null=True, blank=True, help_text="활동 설명")
    keywords = ArrayField(
        models.TextField(), null=True, blank=True, help_text="키워드 목록"
    )

    class Meta:
        db_table = "activity"


class Event(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    situation = models.TextField(null=True, blank=True)
    task = models.TextField(null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    contribution = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_name = models.TextField()

    class Meta:
        db_table = "event"


class ActivityEmbedding(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    metadata = models.JSONField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    embedding = VectorField(dimensions=1536)
    favorite = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity_embedding"
