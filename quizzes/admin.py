from django.contrib import admin
from .models import Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer


class OptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order', 'points')
    list_filter = ('quiz',)
    inlines = [OptionInline]


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'pass_score', 'is_published')
    list_filter = ('is_published', 'course')
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score_percent', 'is_passed', 'is_completed', 'submitted_at')
    list_filter = ('is_passed', 'is_completed', 'quiz')
    search_fields = ('student__username', 'quiz__title')


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option')
