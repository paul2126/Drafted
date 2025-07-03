from django.db import models
from django.contrib.postgres.fields import ArrayField  # postgress specific
from users.models import Profile


class Activity(models.Model):
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    metadata = models.JSONField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity"
