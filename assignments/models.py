from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    attachment = models.FileField(upload_to='assignments/briefs/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def is_past_due(self):
        return timezone.now() > self.due_date


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('resubmission_requested', 'Resubmission Requested'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    file = models.FileField(upload_to='assignments/submissions/')
    notes = models.TextField(blank=True)
    score = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_assignments')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({self.status})"

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date
