from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from courses.models import CourseCategory, Course, Module, Lesson, LearningMaterial, Enrollment, LessonProgress
from assignments.models import Assignment, AssignmentSubmission
from quizzes.models import Quiz, Question, QuestionOption, QuizAttempt
from notifications.models import Announcement, Notification
from analytics.models import LearningActivity


class Command(BaseCommand):
    help = 'Seeds initial demonstration data into SmartLearn LMS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting SmartLearn seed data process...'))

        # 1. Create Admin
        admin_user, created = User.objects.get_or_create(
            username='admin@smartlearn.com',
            defaults={
                'email': 'admin@smartlearn.com',
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.profile.role = 'admin'
            admin_user.profile.department = 'System Operations'
            admin_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created Admin: admin@smartlearn.com (pwd: admin123)'))

        # 2. Create Faculty
        faculty_user, created = User.objects.get_or_create(
            username='dr.smith@smartlearn.com',
            defaults={
                'email': 'dr.smith@smartlearn.com',
                'first_name': 'Alan',
                'last_name': 'Smith',
                'is_staff': False,
            }
        )
        if created:
            faculty_user.set_password('faculty123')
            faculty_user.save()
            faculty_user.profile.role = 'faculty'
            faculty_user.profile.department = 'Computer Science & AI'
            faculty_user.profile.bio = 'Ph.D. in Distributed Systems with 12+ years teaching software engineering and cloud architecture.'
            faculty_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created Faculty: dr.smith@smartlearn.com (pwd: faculty123)'))

        # 3. Create Student
        student_user, created = User.objects.get_or_create(
            username='student@smartlearn.com',
            defaults={
                'email': 'student@smartlearn.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'is_staff': False,
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
            student_user.profile.role = 'student'
            student_user.profile.department = 'Software Engineering'
            student_user.profile.student_id = 'SL-2026-8841'
            student_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created Student: student@smartlearn.com (pwd: student123)'))

        # 4. Categories
        cat_cs, _ = CourseCategory.objects.get_or_create(
            name='Computer Science',
            defaults={'slug': 'computer-science', 'description': 'Foundational algorithms, data structures, and architecture.', 'icon': 'bi-code-slash'}
        )
        cat_ai, _ = CourseCategory.objects.get_or_create(
            name='AI & Machine Learning',
            defaults={'slug': 'ai-machine-learning', 'description': 'Neural networks, generative models, and LLM orchestration.', 'icon': 'bi-cpu'}
        )
        cat_fullstack, _ = CourseCategory.objects.get_or_create(
            name='Full-Stack Web',
            defaults={'slug': 'full-stack-web', 'description': 'Modern web development with Python, Django, REST APIs, and modern frontends.', 'icon': 'bi-layers'}
        )

        # 5. Course: Python & Django Architecture
        c1, created = Course.objects.get_or_create(
            title='Production Django & REST API Architecture',
            defaults={
                'slug': 'production-django-rest-api',
                'category': cat_fullstack,
                'instructor': faculty_user,
                'difficulty': 'intermediate',
                'estimated_hours': 18,
                'is_published': True,
                'short_description': 'Build resilient, scalable backends using Django 5, DRF, MySQL, and enterprise security patterns.',
                'description': 'This master course teaches you how to design, develop, and deploy production-grade Python web backends. You will learn relational database modeling with MySQL, performant RESTful APIs, role-based authorization, and secure session management.',
            }
        )

        if created:
            # Modules for Course 1
            m1 = Module.objects.create(course=c1, title='Module 1: Django Architectural Foundations', order=1)
            l1_1 = Lesson.objects.create(
                module=m1,
                title='Django MVT Architecture & Project Layout',
                order=1,
                duration_minutes=25,
                content='Welcome to the foundational module. Django organizes web applications using Model-View-Template (MVT). Models define database tables and constraints. Views act as controllers handling incoming requests and returning responses. Templates render client-side HTML interfaces.\n\nIn this lesson, you will configure environment variables, secure secret keys, and structure modular multi-app systems.',
                video_url='https://www.youtube.com/embed/rHux0gMZ3Eg'
            )
            l1_2 = Lesson.objects.create(
                module=m1,
                title='Database Modeling & MySQL Migrations',
                order=2,
                duration_minutes=30,
                content='Relational database design is the bedrock of performant applications. We examine ForeignKeys, OneToOne fields, index optimizations, and database constraints in MySQL.\n\nLearn how to use makemigrations and migrate effectively in CI/CD pipelines.',
                video_url='https://www.youtube.com/embed/rHux0gMZ3Eg'
            )

            m2 = Module.objects.create(course=c1, title='Module 2: RESTful APIs & Serialization', order=2)
            l2_1 = Lesson.objects.create(
                module=m2,
                title='Building Serializers & ViewSets with DRF',
                order=1,
                duration_minutes=35,
                content='Django REST Framework accelerates API development with ModelSerializers, ViewSets, and Routers. Learn how to write secure validation rules and customize response payloads.',
                video_url='https://www.youtube.com/embed/rHux0gMZ3Eg'
            )

            # Assignment for Course 1
            Assignment.objects.create(
                course=c1,
                title='Design a Multi-Tenant Data Model in MySQL',
                description='Construct an ER diagram and write Django models with proper foreign key constraints, indexes, and unique constraints for a multi-role educational platform. Submit your models.py file or zip archive.',
                due_date=timezone.now() + timezone.timedelta(days=4),
                max_score=100,
                created_by=faculty_user
            )

            # Quiz for Course 1
            q1 = Quiz.objects.create(
                course=c1,
                title='Django Core & ORM Fundamentals',
                description='Validate your knowledge of Django request lifecycle, querysets, and database indexes.',
                duration_minutes=15,
                pass_score=70.0,
                max_attempts=3,
                is_published=True,
                created_by=faculty_user
            )

            # Question 1
            ques1 = Question.objects.create(
                quiz=q1,
                text='Which setting in Django ensures database transactions are executed against strict table schemas in MySQL?',
                explanation='STRICT_TRANS_TABLES enforces valid data types and rejects invalid truncation or zero dates.',
                order=1,
                points=2
            )
            QuestionOption.objects.create(question=ques1, text='SET sql_mode="STRICT_TRANS_TABLES"', is_correct=True, order=1)
            QuestionOption.objects.create(question=ques1, text='SET autocommit=0', is_correct=False, order=2)
            QuestionOption.objects.create(question=ques1, text='SET innodb_strict_mode=0', is_correct=False, order=3)

            # Question 2
            ques2 = Question.objects.create(
                quiz=q1,
                text='What is the primary difference between select_related and prefetch_related in Django ORM?',
                explanation='select_related uses SQL JOINs for single-valued relationships (ForeignKey, OneToOne), while prefetch_related executes a separate query with Python-level joining for multi-valued relationships (ManyToMany, reverse FK).',
                order=2,
                points=3
            )
            QuestionOption.objects.create(question=ques2, text='select_related performs SQL JOIN; prefetch_related performs a separate SQL lookup', is_correct=True, order=1)
            QuestionOption.objects.create(question=ques2, text='prefetch_related only works on SQLite databases', is_correct=False, order=2)
            QuestionOption.objects.create(question=ques2, text='select_related is deprecated in Django 5', is_correct=False, order=3)

        # 6. Course: Deep Learning & Modern AI
        c2, created2 = Course.objects.get_or_create(
            title='Practical Deep Learning & Neural Networks',
            defaults={
                'slug': 'practical-deep-learning',
                'category': cat_ai,
                'instructor': faculty_user,
                'difficulty': 'advanced',
                'estimated_hours': 24,
                'is_published': True,
                'short_description': 'Master transformer architectures, backpropagation mathematics, and fine-tuning open-source LLMs.',
                'description': 'A comprehensive dive into modern artificial intelligence. Covers linear algebra intuition, backpropagation, attention mechanisms, and practical PyTorch workflows.',
            }
        )

        if created2:
            m_ai = Module.objects.create(course=c2, title='Module 1: Mathematical Foundations', order=1)
            Lesson.objects.create(
                module=m_ai,
                title='Tensors, Matrices, and Gradient Descent',
                order=1,
                duration_minutes=40,
                content='Understand computational graphs, automatic differentiation, and loss landscape optimization.',
                video_url='https://www.youtube.com/embed/rHux0gMZ3Eg'
            )

        # 7. Enroll Student in Course 1
        enrollment, _ = Enrollment.objects.get_or_create(
            student=student_user,
            course=c1,
            defaults={'progress_percent': 50, 'is_active': True}
        )
        # Mark first lesson completed
        first_lesson = c1.modules.first().lessons.first()
        if first_lesson:
            LessonProgress.objects.get_or_create(
                student=student_user,
                lesson=first_lesson,
                defaults={'completed': True, 'completed_at': timezone.now()}
            )
            enrollment.recalculate_progress()

        # 8. Create Campus Announcements
        Announcement.objects.get_or_create(
            title='Welcome to the SmartLearn Academic Term',
            defaults={
                'content': 'We are thrilled to launch the new semester with upgraded interactive courses, smart recommendation pipelines, and instant assessment grading.',
                'target_role': 'all',
                'created_by': admin_user,
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS('SmartLearn demonstration data successfully populated!'))
