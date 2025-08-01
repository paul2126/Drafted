from rest_framework import serializers

class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(source="question", help_text="문항 내용")
    max_characters = serializers.IntegerField(source="max_length" , help_text="분량 제한")

class ApplicationCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    activity = serializers.CharField(source="activity_name", help_text="지원서 제목")
    category = serializers.CharField(help_text="지원서 카테고리")
    enddate = serializers.DateTimeField(source="end_date", help_text="지원서 마감일")
    position = serializers.CharField(
          source="position", help_text="활동 역할 및 직책"
    )
    notice = serializers.CharField(required=False, help_text="모집공고 링크 또는 공고 내용")
    questions = QuestionSerializer(many=True, help_text="지원서 문항 목록")


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, help_text="활동 ID")
    title = serializers.CharField(help_text="활동명")
    activity = serializers.CharField(help_text="활동 진행 기관 (ex. 패스트캠퍼스)")
    comment = serializers.CharField(help_text="AI가 활동을 추천하는 이유 (추천 코멘트)")
    is_recommended = serializers.BooleanField(help_text="추천 여부")


class EventRecommendSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="문항 번호(FK)")
    suggestion = serializers.CharField(help_text="AI가 제안하는 답변")
    eventlist = EventSerializer(many=True, help_text="관련 활동 목록")
