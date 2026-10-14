"""
URL configuration for SmartLearn project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path('admin-panel/', admin.site.urls),

    # SmartLearn apps
    path('accounts/', include('accounts.urls')),
    path('', include('courses.urls')),
    path('assignments/', include('assignments.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('analytics/', include('analytics.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('notifications/', include('notifications.urls')),

    # REST API
    path('api/accounts/', include('accounts.api_urls')),
    path('api/courses/', include('courses.api_urls')),
    path('api/assignments/', include('assignments.api_urls')),
    path('api/quizzes/', include('quizzes.api_urls')),
    path('api/analytics/', include('analytics.api_urls')),
    path('api/recommendations/', include('recommendations.api_urls')),
    path('api/notifications/', include('notifications.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
