from rest_framework.permissions import BasePermission
from rest_framework.authentication import get_authorization_header


class IsSupabaseAuthenticated(BasePermission):
    def has_permission(self, request, view):
        auth_header = get_authorization_header(request).decode("utf-8")
        token = (
            auth_header.replace("Bearer ", "")
            if auth_header.startswith("Bearer ")
            else None
        )
        return token is not None
