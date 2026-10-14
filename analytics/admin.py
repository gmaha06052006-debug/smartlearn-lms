from django.contrib import admin
from .models import LearningActivity, StudySession


@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity_type', 'description', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('student__username', 'description')


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'duration_minutes', 'started_at')
    list_filter = ('course', 'started_at')
