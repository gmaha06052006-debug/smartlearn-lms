from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import LearningActivityViewSet, StudySessionViewSet

router = DefaultRouter()
router.register('activities', LearningActivityViewSet, basename='api_activity')
router.register('study-sessions', StudySessionViewSet, basename='api_study_session')

urlpatterns = [
    path('', include(router.urls)),
]
