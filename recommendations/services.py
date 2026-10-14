from django.utils import timezone
from courses.models import Course, Enrollment, Lesson, LessonProgress
from assignments.models import Assignment, AssignmentSubmission
from quizzes.models import Quiz, QuizAttempt
from .models import Recommendation


class RecommendationEngine:
    """Smart recommendation system that analyzes student learning patterns."""

    @classmethod
    def generate_recommendations_for_user(cls, user):
        """Analyze student state and create up-to-date recommendations."""
        if not user.is_authenticated:
            return []

        # 1. Check upcoming assignments due within 3 days without submission
        now = timezone.now()
        three_days_later = now + timezone.timedelta(days=3)
        enrolled_course_ids = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)

        pending_assignments = Assignment.objects.filter(
            course_id__in=enrolled_course_ids,
            due_date__gte=now,
            due_date__lte=three_days_later
        ).exclude(
            submissions__student=user
        )

        for assign in pending_assignments:
            Recommendation.objects.get_or_create(
                student=user,
                title=f"Due Soon: {assign.title}",
                defaults={
                    'course': assign.course,
                    'reason': f"Assignment '{assign.title}' is due {assign.due_date.strftime('%b %d, %H:%M')}. Submit early to ensure full marks.",
                    'priority': 'high',
                    'action_url': f"/assignments/{assign.id}/",
                }
            )

        # 2. Check next uncompleted lesson in enrolled courses
        enrollments = Enrollment.objects.filter(student=user, is_active=True, progress_percent__lt=100)
        for enrollment in enrollments:
            course = enrollment.course
            completed_lesson_ids = set(
                LessonProgress.objects.filter(student=user, lesson__module__course=course, completed=True).values_list('lesson_id', flat=True)
            )
            next_lesson = Lesson.objects.filter(module__course=course).exclude(id__in=completed_lesson_ids).order_by('module__order', 'order').first()
            if next_lesson:
                Recommendation.objects.get_or_create(
                    student=user,
                    lesson=next_lesson,
                    defaults={
                        'course': course,
                        'title': f"Next Step: {next_lesson.title}",
                        'reason': f"Continue your progress in '{course.title}'. Complete '{next_lesson.title}' ({next_lesson.duration_minutes} mins).",
                        'priority': 'medium',
                        'action_url': f"/courses/{course.slug}/lessons/{next_lesson.id}/",
                    }
                )

        # 3. Check unattempted quizzes in enrolled courses
        quizzes = Quiz.objects.filter(course_id__in=enrolled_course_ids, is_published=True).exclude(
            attempts__student=user, attempts__is_passed=True
        )
        for qz in quizzes[:2]:
            Recommendation.objects.get_or_create(
                student=user,
                title=f"Test Your Knowledge: {qz.title}",
                defaults={
                    'course': qz.course,
                    'reason': f"Strengthen retention by taking the '{qz.title}' assessment in {qz.course.title}.",
                    'priority': 'low',
                    'action_url': f"/quizzes/{qz.id}/start/",
                }
            )

        return Recommendation.objects.filter(student=user, is_dismissed=False).order_by('-priority', '-created_at')[:5]
