from rest_framework import serializers


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
    startDate = serializers.DateTimeField(source="start_date", help_text="활동 시작일")
    endDate = serializers.DateTimeField(source="end_date", help_text="활동 종료일")
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
    keywords = serializers.CharField(required=False, help_text="활동 키워드")
    isFavorite = serializers.BooleanField(
        source="favorite", default=False, required=False, help_text="즐겨찾기 여부"
    )
