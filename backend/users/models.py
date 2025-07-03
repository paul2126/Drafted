from django.db import models


class SupabaseUser(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sign_in_at = models.DateTimeField(null=True)
    # Add other fields as needed from Supabase schema

    class Meta:
        db_table = '"auth"."users"'  # accessing auth schema users table
        managed = False  # VERY IMPORTANT: Django won't try to modify this table


class Profile(models.Model):
    user_id = models.OneToOneField(
        SupabaseUser,
        db_column="user_id",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    university = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    avatar_url = models.CharField(max_length=255)

    class Meta:
        db_table = "profile"  # name of the table
