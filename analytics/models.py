from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class LearningActivity(models.Model):
    ACTIVITY_TYPES = [
        ('enrollment', 'Course Enrollment'),
        ('lesson_completed', 'Lesson Completed'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('assignment_submit', 'Assignment Submitted'),
        ('login', 'User Login'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'learning_activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username}: {self.description} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class StudySession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'study_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.duration_minutes}m)"
