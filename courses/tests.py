from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from courses.models import CourseCategory, Course, Module, Lesson, Enrollment, LessonProgress


class CoursesTestCase(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor@smartlearn.com',
            email='instructor@smartlearn.com',
            password='testpassword123',
            first_name='Prof',
            last_name='Xavier'
        )
        self.instructor.profile.role = 'faculty'
        self.instructor.profile.save()

        self.student = User.objects.create_user(
            username='learner@smartlearn.com',
            email='learner@smartlearn.com',
            password='testpassword123',
            first_name='Bobby',
            last_name='Drake'
        )

        self.category = CourseCategory.objects.create(name='Web Engineering')
        self.course = Course.objects.create(
            title='Full-Stack Mastery',
            category=self.category,
            instructor=self.instructor,
            difficulty='intermediate',
            description='Test course description'
        )
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson1 = Lesson.objects.create(module=self.module, title='Lesson 1', order=1)
        self.lesson2 = Lesson.objects.create(module=self.module, title='Lesson 2', order=2)

    def test_course_slug_auto_generation(self):
        """Test slug is automatically generated from title."""
        self.assertEqual(self.course.slug, 'full-stack-mastery')

    def test_course_total_lessons(self):
        """Test total_lessons property."""
        self.assertEqual(self.course.total_lessons, 2)

    def test_enrollment_progress_recalculation(self):
        """Test enrollment progress updates on lesson completion."""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(enrollment.progress_percent, 0)

        # Mark lesson 1 completed
        LessonProgress.objects.create(student=self.student, lesson=self.lesson1, completed=True)
        enrollment.recalculate_progress()
        self.assertEqual(enrollment.progress_percent, 50)

        # Mark lesson 2 completed
        LessonProgress.objects.create(student=self.student, lesson=self.lesson2, completed=True)
        enrollment.recalculate_progress()
        self.assertEqual(enrollment.progress_percent, 100)

    def test_course_catalog_view(self):
        """Test course catalog response."""
        client = Client()
        response = client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Full-Stack Mastery')
