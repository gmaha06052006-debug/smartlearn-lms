from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import RecommendationViewSet

router = DefaultRouter()
router.register('items', RecommendationViewSet, basename='api_recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
