from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder', help_text='Bootstrap Icon class (e.g. bi-code-slash)')

    class Meta:
        db_table = 'course_categories'
        verbose_name_plural = 'Course Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_courses')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_hours = models.PositiveIntegerField(default=10)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'course_modules'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, help_text='Markdown/HTML lesson content')
    video_url = models.URLField(blank=True, help_text='YouTube/Vimeo embed or MP4 URL')
    duration_minutes = models.PositiveIntegerField(default=15)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'course_lessons'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    @property
    def course(self):
        return self.module.course


class LearningMaterial(models.Model):
    MATERIAL_TYPES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Document'),
        ('link', 'External Link'),
        ('code', 'Source Code'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='courses/materials/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES, default='pdf')

    class Meta:
        db_table = 'course_materials'

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    progress_percent = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_enrollments'
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.progress_percent}%)"

    def recalculate_progress(self):
        total = self.course.total_lessons
        if total == 0:
            self.progress_percent = 100
            if not self.completed_at:
                self.completed_at = timezone.now()
        else:
            completed = LessonProgress.objects.filter(
                student=self.student,
                lesson__module__course=self.course,
                completed=True
            ).count()
            self.progress_percent = min(100, int((completed / total) * 100))
            if self.progress_percent >= 100:
                if not self.completed_at:
                    self.completed_at = timezone.now()
            else:
                self.completed_at = None
        self.save(update_fields=['progress_percent', 'completed_at'])
        return self.progress_percent

    @property
    def completed_lessons_count(self):
        return LessonProgress.objects.filter(
            student=self.student,
            lesson__module__course=self.course,
            completed=True
        ).count()


class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'course_lesson_progress'
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({'Done' if self.completed else 'Pending'})"
