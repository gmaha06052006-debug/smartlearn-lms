from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AssignmentViewSet, AssignmentSubmissionViewSet

router = DefaultRouter()
router.register('items', AssignmentViewSet, basename='api_assignment')
router.register('submissions', AssignmentSubmissionViewSet, basename='api_submission')

urlpatterns = [
    path('', include(router.urls)),
]
