from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from courses.models import Enrollment, LessonProgress
from .models import LearningActivity, StudySession


@login_required
def analytics_dashboard_view(request):
    """Student performance analytics view."""
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')

    course_names = [e.course.title[:20] for e in enrollments]
    course_progress = [e.progress_percent for e in enrollments]

    total_study_minutes = StudySession.objects.filter(student=user).aggregate(total=Sum('duration_minutes'))['total'] or 0

    recent_activities = LearningActivity.objects.filter(student=user).order_by('-created_at')[:10]

    context = {
        'page_title': 'Learning Analytics',
        'enrollments': enrollments,
        'course_names': course_names,
        'course_progress': course_progress,
        'total_study_minutes': total_study_minutes,
        'recent_activities': recent_activities,
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def api_chart_data(request):
    """JSON endpoint for dynamic Chart.js rendering."""
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')

    data = {
        'labels': [e.course.title for e in enrollments],
        'progress': [e.progress_percent for e in enrollments],
    }
    return JsonResponse(data)
