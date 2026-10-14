from django.contrib import admin
from .models import CourseCategory, Course, Module, Lesson, LearningMaterial, Enrollment, LessonProgress


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1


class MaterialInline(admin.StackedInline):
    model = LearningMaterial
    extra = 1


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'difficulty', 'is_published', 'created_at')
    list_filter = ('difficulty', 'is_published', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration_minutes')
    list_filter = ('module__course',)
    inlines = [MaterialInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_percent', 'is_active', 'enrolled_at')
    list_filter = ('is_active', 'course')
    search_fields = ('student__username', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed',)
