from users.models import Profile
from django.db import models


class ChatSession(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_session"

    def __str__(self):
        return f"Chat Session: {self.title} (User: {self.user_id})"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        db_column="session_id",
    )
    role = models.TextField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_message"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
