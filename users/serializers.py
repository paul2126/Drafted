from rest_framework import serializers


class ProfileInfoSerializer(serializers.Serializer):
    user_id = serializers.CharField(read_only=True, help_text="유저 id")
    name = serializers.CharField(required=False, help_text="이름")
    university = serializers.CharField(required=False, help_text="대학교")
    major = serializers.CharField(required=False, help_text="전공")
    graduation_year = serializers.IntegerField(
        required=False, help_text="졸업 예정 연도"
    )
    field_of_interest = serializers.CharField(required=False, help_text="관심 분야")
