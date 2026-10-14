from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import NotificationViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register('items', NotificationViewSet, basename='api_notification')
router.register('announcements', AnnouncementViewSet, basename='api_announcement')

urlpatterns = [
    path('', include(router.urls)),
]
