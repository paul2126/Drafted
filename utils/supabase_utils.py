from supabase import create_client
from rest_framework.authentication import get_authorization_header
from django.conf import settings
import jwt


def get_supabase_client(request):
    """Create authenticated Supabase client"""
    auth_header = get_authorization_header(request).decode("utf-8")
    token = (
        auth_header.replace("Bearer ", "")
        if auth_header.startswith("Bearer ")
        else None
    )

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    if token:
        supabase.postgrest.auth(token)
    return supabase


def get_user_id_from_token(request):
    auth_header = get_authorization_header(request).decode("utf-8")
    token = (
        auth_header.replace("Bearer ", "")
        if auth_header.startswith("Bearer ")
        else None
    )

    if token:
        # Decode without verification (Supabase RLS handles verification)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")  # User ID from JWT
    return None
