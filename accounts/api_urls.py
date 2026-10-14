from django.urls import path
from .api_views import CurrentUserAPIView

urlpatterns = [
    path('me/', CurrentUserAPIView.as_view(), name='api_current_user'),
]
