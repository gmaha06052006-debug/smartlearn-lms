from django.contrib import admin
from .models import Assignment, AssignmentSubmission


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ('student', 'submitted_at')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_score', 'created_by')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')
    inlines = [AssignmentSubmissionInline]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')
