from supabase import create_client
from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ProfileInfoSerializer
from utils.supabase_utils import get_supabase_client, get_user_id_from_token


class ProfileInfoView(APIView):
    def filter_fields(self, data):
        # Filter the fields to match the serializer
        return {
            "name": data.get("name"),
            "university": data.get("university"),
            "major": data.get("major"),
            "graduation_year": data.get("graduation_year"),
            "field_of_interest": data.get("field_of_interest"),
        }

    @swagger_auto_schema(
        operation_description="Get user profile information",
        responses={200: ProfileInfoSerializer(many=False)},
        tags=["Profile"],
    )
    def get(self, request, user_id):
        supabase = get_supabase_client(request)

        # Query through Supabase (respects RLS)
        result = supabase.table("profile").select("*").eq("user_id", user_id).execute()

        if not result.data:
            return Response({"error": "Profile not found"}, status=404)

        return Response(self.filter_fields(result.data[0]), status=200)

    @swagger_auto_schema(
        operation_description="Update user profile information",
        request_body=ProfileInfoSerializer,
        responses={200: ProfileInfoSerializer(many=False)},
        tags=["Profile"],
    )
    def post(self, request, user_id):
        supabase = get_supabase_client(request)

        # Extract data from request
        data = request.data

        # Update profile in Supabase
        result = supabase.table("profile").update(data).eq("user_id", user_id).execute()

        if not result.data:
            return Response({"error": "Profile not found or update failed"}, status=404)

        return Response(self.filter_fields(result.data[0]), status=200)

    @swagger_auto_schema(
        operation_description="Delete user profile",
        responses={204: "Profile deleted successfully"},
        tags=["Profile"],
    )
    def delete(self, request, user_id):
        supabase = get_supabase_client(request)

        # Delete profile in Supabase
        result = supabase.table("profile").delete().eq("user_id", user_id).execute()

        if not result.data:
            return Response(
                {"error": "Profile not found or deletion failed"}, status=404
            )

        return Response({"message": "Profile deleted successfully"}, status=204)
