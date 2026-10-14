from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'priority', 'is_dismissed', 'created_at')
    list_filter = ('priority', 'is_dismissed')
    search_fields = ('student__username', 'title', 'reason')
