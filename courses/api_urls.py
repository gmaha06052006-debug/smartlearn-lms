from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CourseCategoryViewSet, CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register('categories', CourseCategoryViewSet, basename='api_category')
router.register('courses', CourseViewSet, basename='api_course')
router.register('enrollments', EnrollmentViewSet, basename='api_enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
