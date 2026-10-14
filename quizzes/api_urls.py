from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import QuizViewSet, QuizAttemptViewSet

router = DefaultRouter()
router.register('quizzes', QuizViewSet, basename='api_quiz')
router.register('attempts', QuizAttemptViewSet, basename='api_quiz_attempt')

urlpatterns = [
    path('', include(router.urls)),
]
