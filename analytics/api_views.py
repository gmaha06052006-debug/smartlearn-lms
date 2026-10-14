from rest_framework import viewsets, permissions
from .models import LearningActivity, StudySession
from .serializers import LearningActivitySerializer, StudySessionSerializer


class LearningActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LearningActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningActivity.objects.filter(student=self.request.user)


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
