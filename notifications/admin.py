from django.contrib import admin
from .models import Notification, Announcement


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title', 'message')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_role', 'is_active', 'created_by', 'created_at')
    list_filter = ('target_role', 'is_active')
    search_fields = ('title', 'content')
