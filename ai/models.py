from django.db import models
from applications.models import QuestionList
from activities.models import Event


class EventSuggestion(models.Model):
    question = models.ForeignKey(QuestionList, on_delete=models.CASCADE)
    activity = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        db_table = "event_suggestion"
