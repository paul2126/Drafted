from rest_framework import serializers
from .models import Profile


class ProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["name", "university", "major", "graduation_year", "field_of_interest"]
