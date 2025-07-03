from django.db import models
from pgvector.django import VectorField

# from django.contrib.postgres.fields import ArrayField  # postgress specific
from users.models import Profile


class ActivityEmbedding(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    metadata = models.JSONField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    embedding = VectorField(dimensions=3072)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity_embedding"


class Activity(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "activity"


class Event(models.Model):
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    role = models.TextField(null=True, blank=True)
    ability = models.TextField(null=True, blank=True)
    background = models.TextField(null=True, blank=True)
    my_action = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    reflection = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "event"
