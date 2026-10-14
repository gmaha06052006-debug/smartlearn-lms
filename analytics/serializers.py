from rest_framework import serializers
from .models import LearningActivity, StudySession


class LearningActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningActivity
        fields = '__all__'


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = '__all__'
