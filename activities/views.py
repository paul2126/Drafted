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
    EventSerializer,
    EventCreateUpdateSerializer,
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
                "title": activity.get("activity_name"),
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
            activities = self._get_all_activities(supabase, request)
            return Response(
                {"activities": activities},
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

        # Validate request data and remap fields to match the database schema
        serializer = ActivityCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get validated data (this ensures proper datetime handling)
        validated_data = serializer.validated_data
        validated_data["user_id"] = user_id

        # Convert datetime objects to ISO format strings for Supabase
        for key, value in validated_data.items():
            if hasattr(value, "isoformat"):  # Check if it's a datetime object
                validated_data[key] = value.isoformat()

        result = supabase.table("activity").insert(validated_data).execute()

        if not result.data:
            return Response(
                {"error": "Failed to create activity"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result.data[0], status=status.HTTP_201_CREATED)


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
            print(
                f"Fetching details for activity_id: {activity_id}, user_id: {user_id}"
            )
            # Call stored procedure - automatically updates last_visit
            result = supabase.rpc(
                "get_activity_detail",
                {"p_activity_id": activity_id, "p_user_id": user_id},
            ).execute()

            if not result.data:
                return Response(
                    {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
                )
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
                {"error": "Activity not found or update failed"},
                status=status.HTTP_404_NOT_FOUND,
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

        # # Regular partial update
        # update_data = {k: v for k, v in request.data.items() if v is not None}
        # Use the serializer to validate and map fields
        serializer = ActivityUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get validated data with proper field mapping
        validated_data = serializer.validated_data

        # Convert datetime objects to ISO format for Supabase
        update_data = {}
        for key, value in validated_data.items():
            if value is not None:
                if hasattr(value, "isoformat"):  # datetime objects
                    update_data[key] = value.isoformat()
                else:
                    update_data[key] = value
        result = (
            supabase.table("activity")
            .update(update_data)
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            return Response(
                {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
            )
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

        return (
            Response(status=status.HTTP_204_NO_CONTENT)
            if result.data
            else Response(
                {"error": "Activity not found or deletion failed"},
                status=status.HTTP_404_NOT_FOUND,
            )
        )


class EventListView(APIView):
    @swagger_auto_schema(
        operation_summary="특정 활동에 등록된 이벤트 전체 조회",
        operation_description="특정 활동에 등록된 모든 이벤트를 조회합니다.",
        responses={200: EventSerializer(many=True), 404: "Activity not found"},
        tags=["Event"],
    )
    def get(self, request, activity_id):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Check if activity exists and belongs to user
            activity_result = (
                supabase.table("activity")
                .select("id")
                .eq("id", activity_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not activity_result.data:
                return Response(
                    {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Get all events for this activity
            events_result = (
                supabase.table("event")
                .select("*")
                .eq("activity_id", activity_id)
                .order("created_at", desc=True)
                .execute()
            )

            # Format events data to match specification
            events_data = []
            for event in events_result.data:
                event_data = {
                    "id": str(event.get("id")),
                    "activity": str(activity_id),
                    "title": event.get("event_name"),
                    "situation": event.get("situation"),
                    "task": event.get("task"),
                    "action": event.get("action"),
                    "result": event.get("result"),
                    "startDate": event.get("start_date"),
                    "endDate": event.get("end_date"),
                    "attachedFiles": [],  # TODO: Implement file attachment functionality
                    "createdAt": event.get("created_at"),
                    "updatedAt": event.get("updated_at"),
                }
                events_data.append(event_data)

            return Response(events_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Failed to fetch events", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="특정 활동에 새로운 이벤트 추가",
        operation_description="특정 활동에 새로운 이벤트를 추가합니다.",
        request_body=EventCreateUpdateSerializer,
        responses={
            201: openapi.Response(
                "Created",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"id": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: "Bad Request",
            404: "Activity not found",
        },
        tags=["Event"],
    )
    def post(self, request, activity_id):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Check if activity exists and belongs to user
            activity_result = (
                supabase.table("activity")
                .select("id")
                .eq("id", activity_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not activity_result.data:
                return Response(
                    {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Validate request data
            serializer = EventCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Prepare data for Supabase insertion
            validated_data = serializer.validated_data
            event_data = {
                "activity_id": activity_id,
                "event_name": validated_data.get("event_name"),
                "situation": validated_data.get("situation"),
                "task": validated_data.get("task"),
                "action": validated_data.get("action"),
                "result": validated_data.get("result"),
                "start_date": (
                    validated_data.get("start_date").isoformat()
                    if validated_data.get("start_date")
                    else None
                ),
                "end_date": (
                    validated_data.get("end_date").isoformat()
                    if validated_data.get("end_date")
                    else None
                ),
            }

            # Insert event
            result = supabase.table("event").insert(event_data).execute()

            if not result.data:
                return Response(
                    {"error": "Failed to create event"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"id": str(result.data[0]["id"])}, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": "Failed to create event", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="기존 이벤트 정보 수정",
        operation_description="기존 이벤트(STAR+@)를 수정합니다.",
        request_body=EventCreateUpdateSerializer,
        responses={
            200: openapi.Response(
                "Updated",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_STRING),
                        "updatedAt": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                    },
                ),
            ),
            400: "Bad Request",
            404: "Event not found",
        },
        tags=["Event"],
    )
    def patch(self, request, activity_id, event_id):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Check if activity exists and belongs to user
            activity_result = (
                supabase.table("activity")
                .select("id")
                .eq("id", activity_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not activity_result.data:
                return Response(
                    {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Check if event exists and belongs to the activity
            event_result = (
                supabase.table("event")
                .select("id")
                .eq("id", event_id)
                .eq("activity_id", activity_id)
                .execute()
            )

            if not event_result.data:
                return Response(
                    {"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Validate request data
            serializer = EventCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Prepare update data for Supabase
            validated_data = serializer.validated_data
            update_data = {}

            if "event_name" in validated_data:
                update_data["event_name"] = validated_data["event_name"]
            if "situation" in validated_data:
                update_data["situation"] = validated_data["situation"]
            if "task" in validated_data:
                update_data["task"] = validated_data["task"]
            if "action" in validated_data:
                update_data["action"] = validated_data["action"]
            if "result" in validated_data:
                update_data["result"] = validated_data["result"]
            if "start_date" in validated_data and validated_data["start_date"]:
                update_data["start_date"] = validated_data["start_date"].isoformat()
            if "end_date" in validated_data and validated_data["end_date"]:
                update_data["end_date"] = validated_data["end_date"].isoformat()

            # Update event
            result = (
                supabase.table("event")
                .update(update_data)
                .eq("id", event_id)
                .eq("activity_id", activity_id)
                .execute()
            )

            if not result.data:
                return Response(
                    {"error": "Failed to update event"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "id": str(result.data[0]["id"]),
                    "updatedAt": result.data[0]["updated_at"],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to update event", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="이벤트 삭제",
        operation_description="특정 이벤트를 삭제합니다.",
        responses={204: "No Content", 404: "Event not found"},
        tags=["Event"],
    )
    def delete(self, request, activity_id, event_id):
        try:
            supabase = get_supabase_client(request)
            user_id = get_user_id_from_token(request)

            # Check if activity exists and belongs to user
            activity_result = (
                supabase.table("activity")
                .select("id")
                .eq("id", activity_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not activity_result.data:
                return Response(
                    {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Check if event exists and belongs to the activity
            event_result = (
                supabase.table("event")
                .select("id")
                .eq("id", event_id)
                .eq("activity_id", activity_id)
                .execute()
            )

            if not event_result.data:
                return Response(
                    {"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Delete event
            result = (
                supabase.table("event")
                .delete()
                .eq("id", event_id)
                .eq("activity_id", activity_id)
                .execute()
            )

            return (
                Response(status=status.HTTP_204_NO_CONTENT)
                if result.data
                else Response(
                    {"error": "Event not found or deletion failed"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            )

        except Exception as e:
            return Response(
                {"error": "Failed to delete event", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
