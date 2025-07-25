from django.db import models
from pgvector.django import VectorField

# from django.contrib.postgres.fields import ArrayField  # postgress specific
from users.models import Profile


class ActivityEmbedding(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    metadata = models.JSONField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    embedding = VectorField(dimensions=1536)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity_embedding"


class Activity(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    activity_name = models.TextField()
    category = models.TextField(null=True, blank=True)
    position = models.TextField(null=True, blank=True)
    file_list = models.JSONField(null=True, blank=True)  # List of file URLs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

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
