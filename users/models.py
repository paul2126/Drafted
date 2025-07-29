from django.db import models


class Profile(models.Model):
    user_id = models.TextField(primary_key=True)  # Unique identifier for the user
    name = models.TextField()
    university = models.TextField()
    major = models.TextField()
    graduation_year = models.IntegerField()
    field_of_interest = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profile"  # name of the table
