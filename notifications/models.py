from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'Assignment Due'),
        ('grade', 'Grade Published'),
        ('course', 'Course Update'),
        ('announcement', 'Announcement'),
        ('system', 'System Notice'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"


class Announcement(models.Model):
    TARGET_ROLES = [
        ('all', 'Everyone'),
        ('student', 'Students Only'),
        ('faculty', 'Faculty Only'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    target_role = models.CharField(max_length=15, choices=TARGET_ROLES, default='all')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
