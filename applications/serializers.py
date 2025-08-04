from rest_framework import serializers
from .models import Application, QuestionList

class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(source="question", help_text="문항 내용")
    max_characters = serializers.IntegerField(source="max_length" , help_text="분량 제한")


class ApplicationCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    activity = serializers.CharField(required=True, source="activity_name", help_text="지원서 제목")
    category = serializers.CharField(help_text="지원서 카테고리")
    endDate = serializers.DateTimeField(source="end_date", help_text="지원서 마감일")
    position = serializers.CharField( help_text="활동 역할 및 직책")
    notice = serializers.CharField(required=False, help_text="모집공고 링크 또는 공고 내용")
    questions = QuestionSerializer(many=True, help_text="지원서 문항 목록")


class ApplicationListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="activity_name", read_only=True)
    deadline = serializers.DateField(source="end_date", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "title", "category", "position", "deadline", "createdAt"]


class ApplicationDetailQuestionSerializer(serializers.ModelSerializer):
    questionId = serializers.IntegerField(source="id", read_only=True)
    questionOrder = serializers.SerializerMethodField()
    content = serializers.CharField(source="question", read_only=True)
    answer = serializers.CharField(default="", read_only=True)
    limit = serializers.IntegerField(source="max_length", read_only=True)

    class Meta:
        model = QuestionList
        fields = ["questionId", "questionOrder", "content", "answer", "limit"]

    def get_questionOrder(self, obj):
        ordered_qs = obj.application.questionlist_set.order_by("id")
        return list(ordered_qs).index(obj) + 1



class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, help_text="활동 ID")
    title = serializers.CharField(help_text="활동명")
    activity = serializers.CharField(help_text="활동 진행 기관 (ex. 패스트캠퍼스)")
    comment = serializers.CharField(help_text="AI가 활동을 추천하는 이유 (추천 코멘트)")
    is_recommended = serializers.BooleanField(help_text="추천 여부")


#ai
class QuestionGuideSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="문항 번호(FK)")
    content = serializers.CharField(help_text="문항별 작성 가이드라인 (AI 생성)")

class EventRecommendSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="문항 번호(FK)")
    suggestion = serializers.CharField(help_text="AI가 제안하는 답변")
    eventlist = EventSerializer(many=True, help_text="관련 활동 목록")

