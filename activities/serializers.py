from rest_framework import serializers
from .models import Activity, Event


class ActivityListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(source="activity_name", help_text="활동 제목")
    category = serializers.CharField(help_text="활동 카테고리")
    startDate = serializers.DateTimeField(
        source="start_date", required=False, help_text="활동 시작일"
    )
    endDate = serializers.DateTimeField(
        source="end_date", required=False, help_text="활동 종료일"
    )
    lastVisit = serializers.DateTimeField(
        source="last_visit", help_text="마지막 확인일"
    )
    isFavorite = serializers.BooleanField(
        source="favorite", default=False, help_text="즐겨찾기 여부"
    )
    recentEvents = serializers.ListField(
        child=serializers.CharField(), help_text="최근 활동 목록"
    )
    event_count = serializers.IntegerField(help_text="활동 개수")


class ActivityRecentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(source="activity_name")


class ActivityDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(source="activity_name", help_text="활동 제목")
    category = serializers.CharField(help_text="활동 카테고리")
    startDate = serializers.DateTimeField(source="start_date", help_text="활동 시작일",allow_null=True, required=False)
    endDate = serializers.DateTimeField(source="end_date", help_text="활동 종료일",allow_null=True, required=False)
    role = serializers.CharField(
        source="position",
    )
    description = serializers.CharField(help_text="활동 설명")
    keywords = serializers.CharField(help_text="활동 키워드")
    isFavorite = serializers.BooleanField(
        source="favorite", default=False, help_text="즐겨찾기 여부"
    )
    createdAt = serializers.DateTimeField(source="created_at", help_text="활동 생성일")
    updatedAt = serializers.DateTimeField(source="updated_at", help_text="활동 수정일")


class ActivityCreateSerializer(serializers.Serializer):
    title = serializers.CharField(source="activity_name", help_text="활동 제목")
    category = serializers.CharField(help_text="활동 카테고리")
    startDate = serializers.DateTimeField(
        source="start_date", required=False, help_text="활동 시작일"
    )
    endDate = serializers.DateTimeField(
        source="end_date", required=False, help_text="활동 종료일"
    )
    role = serializers.CharField(
        source="position", required=False, help_text="활동 역할 및 직책"
    )
    description = serializers.CharField(required=False, help_text="활동 설명")
    keywords = serializers.CharField(required=False, help_text="활동 키워드")
    isFavorite = serializers.BooleanField(
        source="favorite", default=False, help_text="즐겨찾기 여부"
    )


class ActivityUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(
        source="activity_name", required=False, help_text="활동 제목"
    )
    category = serializers.CharField(required=False, help_text="활동 카테고리")
    startDate = serializers.DateTimeField(
        source="start_date", required=False, help_text="활동 시작일"
    )
    endDate = serializers.DateTimeField(
        source="end_date", required=False, help_text="활동 종료일"
    )
    role = serializers.CharField(
        source="position",
    )
    description = serializers.CharField(required=False, help_text="활동 설명")
    keywords = serializers.ListField(                    
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    isFavorite = serializers.BooleanField(
        source="favorite", default=False, required=False, help_text="즐겨찾기 여부"
    )


class EventSerializer(serializers.ModelSerializer):
    activity = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(source="event_name", help_text="이벤트 제목")
    startDate = serializers.DateField(source="start_date", help_text="시작일")
    endDate = serializers.DateField(source="end_date", help_text="종료일")
    attachedFiles = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Event
        ref_name = "ActivityEvent"
        fields = [
            "id",
            "activity",
            "title",
            "situation",
            "task",
            "action",
            "result",
            "startDate",
            "endDate",
            "attachedFiles",
            "createdAt",
            "updatedAt",
        ]

    def get_attachedFiles(self, obj):
        # TODO: Implement file attachment functionality
        return []

    def create(self, validated_data):
        activity_id = self.context.get("activity_id")
        activity = Activity.objects.get(id=activity_id)
        validated_data["activity"] = activity
        return super().create(validated_data)


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="event_name", help_text="이벤트 제목")
    startDate = serializers.DateField(
        source="start_date", required=False, help_text="시작일"
    )
    endDate = serializers.DateField(
        source="end_date", required=False, help_text="종료일"
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "situation",
            "task",
            "action",
            "result",
            "startDate",
            "endDate",
        ]

    def create(self, validated_data):
        activity_id = self.context.get("activity_id")
        activity = Activity.objects.get(id=activity_id)
        validated_data["activity"] = activity
        return super().create(validated_data)
