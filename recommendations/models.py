from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Lesson


class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    reason = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    action_url = models.CharField(max_length=255, blank=True)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.title} ({self.priority})"
