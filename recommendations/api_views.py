from rest_framework import viewsets, permissions
from .models import Recommendation
from .serializers import RecommendationSerializer
from .services import RecommendationEngine


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Trigger dynamic evaluation
        RecommendationEngine.generate_recommendations_for_user(self.request.user)
        return Recommendation.objects.filter(student=self.request.user, is_dismissed=False)
