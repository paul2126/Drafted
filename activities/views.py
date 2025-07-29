from supabase import create_client
from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.supabase_utils import get_supabase_client, get_user_id_from_token
from .serializers import (
    ActivityListSerializer,
    ActivityCreateSerializer,
    ActivityDetailSerializer,
    ActivityUpdateSerializer,
)


class ActivityListView(APIView):
    def _get_all_activities(self, supabase, request):
        """Get all activities with event counts"""
        activities_result = (
            supabase.table("activity")
            .select("*, event!activity_id(*)")  # left join with event table
            .eq("user_id", get_user_id_from_token(request))
            .execute()
        )

        activities_data = []
        for activity in activities_result.data:
            activity_data = {
                "id": activity.get("id"),
                "title": activity.get("name"),
                "category": activity.get("category"),
                "startDate": activity.get("start_date"),
                "endDate": activity.get("end_date"),
                "lastVisit": activity.get("last_visit"),
                "isFavorite": activity.get("favorite", False),
                "recentEvents": activity.get("event", []),
                "event_count": len(activity.get("event", [])),
            }
            activities_data.append(activity_data)

        return activities_data

    def _get_event_by_id(self, supabase, event_id):
        """Get specific event with activities"""
        event_result = (
            supabase.table("event")
            .select("*, activity(*)")
            .eq("id", event_id)
            .execute()
        )

        if not event_result.data:
            return None

        event = event_result.data[0]
        return {**event, "activity_count": len(event.get("activities", []))}

    @swagger_auto_schema(
        operation_summary="사용자의 전체 활동 리스트를 조회",
        operation_description="활동 아카이빙 메인페이지 진입 시, 사용자의 전체 활동 리스트를 조회합니다.",
        responses={200: ActivityListSerializer(many=True)},
        tags=["Activity"],
    )
    def get(self, request):
        """Handle both list and detail views"""
        try:
            supabase = get_supabase_client(request)

            # Get all events
            events = self._get_all_activities(supabase, request)
            return Response(
                {"events": events, "total_events": len(events)},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to fetch events", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="새 활동 생성",
        operation_description="‘+ 활동 추가’ 클릭 후 저장 버튼 클릭 시",
        request_body=ActivityCreateSerializer,
        responses={201: ActivityDetailSerializer(), 400: "Bad Request"},
        tags=["Activity"],
    )
    def post(self, request):
        """Create new activity"""
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        data = request.data
        data["user_id"] = user_id  # Ensure user_id is set

        result = supabase.table("activity").insert(data).execute()

        if not result.data:
            return Response({"error": "Failed to create activity"}, status=400)

        return Response(result.data[0], status=201)


class ActivityDetailView(APIView):
    """Detailed view for a specific activity."""

    @swagger_auto_schema(
        operation_summary="특정 활동의 상세 정보 조회",
        operation_description="활동 카드 클릭 후 상세페이지 진입 시, 특정 활동의 상세 정보를 조회합니다.",
        responses={200: ActivityDetailSerializer(), 404: "Activity not found"},
        tags=["Activity"],
    )
    def get(self, request, activity_id):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Call stored procedure - automatically updates last_visit
            result = supabase.rpc(
                "get_activity_detail",
                {"p_activity_id": activity_id, "p_user_id": user_id},
            ).execute()

            if not result.data:
                return Response({"error": "Activity not found"}, status=404)
            return Response(result.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Failed to fetch events", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update activity",
        request_body=ActivityUpdateSerializer,
        responses={200: ActivityDetailSerializer()},
        tags=["Activity"],
    )
    def put(self, request, activity_id):
        """Full update of activity"""
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        result = (
            supabase.table("activity")
            .update(request.data)
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            return Response(
                {"error": "Activity not found or update failed"}, status=404
            )

        return Response(result.data[0])

    @swagger_auto_schema(
        operation_summary="활동 부분 업데이트",
        operation_description="Partial update activity",
        request_body=ActivityUpdateSerializer,
        responses={200: ActivityDetailSerializer()},
        tags=["Activity"],
    )
    def patch(self, request, activity_id):
        """Partial update - updates only provided fields"""
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        # Regular partial update
        update_data = {k: v for k, v in request.data.items() if v is not None}

        result = (
            supabase.table("activity")
            .update(update_data)
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            return Response({"error": "Activity not found"}, status=404)
        return Response(result.data[0])

    @swagger_auto_schema(
        operation_summary="활동 삭제",
        operation_description="활동 카드에서 휴지통 클릭 시, 해당 활동을 삭제합니다.",
        responses={204: "No Content", 404: "Activity not found"},
        tags=["Activity"],
    )
    def delete(self, request, activity_id):
        """Delete activity"""
        supabase = get_supabase_client(request)
        user_id = get_user_id_from_token(request)

        result = (
            supabase.table("activity")
            .delete()
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        return Response(status=204)
