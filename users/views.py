from supabase import create_client
from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from .serializers import ProfileInfoSerializer
from utils.supabase_utils import get_supabase_client, get_user_id_from_token
from rest_framework import status


class ProfileCreateView(APIView):
    """Create new profile"""

    @swagger_auto_schema(
        operation_summary="프로필 생성",
        operation_description="프로필 생성",
        request_body=ProfileInfoSerializer,
        responses={201: ProfileInfoSerializer(), 400: "Bad Request"},
        tags=["Profile"],
    )
    def post(self, request):
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        serializer = ProfileInfoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data["user_id"] = user_id

        result = supabase.table("profile").insert(data).execute()

        if not result.data:
            return Response(
                {"error": "Failed to create profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            self._filter_fields(result.data[0]), status=status.HTTP_201_CREATED
        )

    def _filter_fields(self, data):
        return {
            "name": data.get("name"),
            "university": data.get("university"),
            "major": data.get("major"),
            "graduation_year": data.get("graduation_year"),
            "field_of_interest": data.get("field_of_interest"),
        }


class ProfileInfoView(APIView):
    def _filter_fields(self, data):
        # Filter the fields to match the serializer
        return {
            "name": data.get("name"),
            "university": data.get("university"),
            "major": data.get("major"),
            "graduation_year": data.get("graduation_year"),
            "field_of_interest": data.get("field_of_interest"),
        }

    @swagger_auto_schema(
        operation_summary="프로필 정보 조회",
        operation_description="프로필 정보 조회",
        responses={200: ProfileInfoSerializer(many=False), 404: "Profile not found"},
        tags=["Profile"],
    )
    def get(self, request):
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        # Query through Supabase (respects RLS)
        result = supabase.table("profile").select("*").eq("user_id", user_id).execute()

        if not result.data:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(self._filter_fields(result.data[0]), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로필 정보 업데이트",
        operation_description="프로필 정보 업데이트",
        request_body=ProfileInfoSerializer,
        responses={200: ProfileInfoSerializer(many=False), 404: "Profile not found"},
        tags=["Profile"],
    )
    def put(self, request):
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        result = (
            supabase.table("profile")
            .update(request.data)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            return Response(
                {"error": "Update failed"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(result.data[0])

    @swagger_auto_schema(
        operation_summary="프로필 제거",
        operation_description="프로필 제거",
        responses={204: "Profile deleted successfully", 404: "Profile not found"},
        tags=["Profile"],
    )
    def delete(self, request):
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        # Delete profile in Supabase
        result = supabase.table("profile").delete().eq("user_id", user_id).execute()

        if not result.data:
            return Response(
                {"error": "Profile not found or deletion failed"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
