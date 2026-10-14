from rest_framework import viewsets, permissions
from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.is_faculty:
            return Assignment.objects.filter(course__instructor=user)
        elif user.profile.is_admin:
            return Assignment.objects.all()
        return Assignment.objects.filter(course__enrollments__student=user, course__enrollments__is_active=True).distinct()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.is_faculty or user.profile.is_admin:
            return AssignmentSubmission.objects.all()
        return AssignmentSubmission.objects.filter(student=user)
