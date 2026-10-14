from rest_framework import serializers
from .models import Assignment, AssignmentSubmission


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = ['submitted_at', 'graded_at', 'graded_by']


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    submissions_count = serializers.IntegerField(source='submissions.count', read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
