from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse

from .models import Course, CourseCategory, Module, Lesson, Enrollment, LessonProgress, LearningMaterial
from analytics.models import LearningActivity


@login_required
def student_dashboard_view(request):
    """Main student dashboard replicating the placed-ai-main-2 portal UI."""
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course', 'course__category', 'course__instructor')
    
    # Calculate stats
    enrolled_count = enrollments.count()
    completed_courses_count = enrollments.filter(progress_percent=100).count()
    
    total_progress = 0
    if enrolled_count > 0:
        total_progress = int(sum(e.progress_percent for e in enrollments) / enrolled_count)

    completed_lessons_count = LessonProgress.objects.filter(student=user, completed=True).count()

    # Recent activities
    activities = LearningActivity.objects.filter(student=user).order_by('-created_at')[:6]

    # In-progress courses (prioritize active, non-completed or recent)
    active_courses = enrollments.order_by('-enrolled_at')[:6]

    context = {
        'page_title': 'Student Dashboard',
        'enrolled_count': enrolled_count,
        'completed_courses_count': completed_courses_count,
        'overall_progress': total_progress,
        'completed_lessons_count': completed_lessons_count,
        'activities': activities,
        'active_courses': active_courses,
    }
    return render(request, 'student/dashboard.html', context)


def course_list_view(request):
    """Catalog of all published courses with search, filtering, and student progress tracking."""
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor').prefetch_related('modules__lessons')
    categories = CourseCategory.objects.annotate(course_count=Count('courses'))

    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(instructor__first_name__icontains=search_query) |
            Q(instructor__last_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    # Check user enrollments and progress
    enrolled_course_ids = set()
    user_enrollments = {}
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
        for enr in enrollments:
            enrolled_course_ids.add(enr.course_id)
            user_enrollments[enr.course_id] = enr

    for course in courses:
        course.user_enrollment = user_enrollments.get(course.id)

    context = {
        'page_title': 'Course Catalog',
        'courses': courses,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'enrolled_course_ids': enrolled_course_ids,
        'user_enrollments': user_enrollments,
    }
    return render(request, 'courses/list.html', context)


def engineering_courses_view(request):
    """Curated showcase of top engineering courses across all engineering disciplines."""
    engineering_categories = CourseCategory.objects.filter(
        Q(name__icontains='Engineering') | 
        Q(name__icontains='Computer Science') |
        Q(name__icontains='AI & Machine Learning') |
        Q(slug__icontains='engineering')
    )
    
    courses = Course.objects.filter(
        is_published=True,
        category__in=engineering_categories
    ).select_related('category', 'instructor').prefetch_related('modules__lessons').order_by('category__name', '-estimated_hours')

    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    enrolled_course_ids = set()
    user_enrollments = {}
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
        for enr in enrollments:
            enrolled_course_ids.add(enr.course_id)
            user_enrollments[enr.course_id] = enr

    for course in courses:
        course.user_enrollment = user_enrollments.get(course.id)

    context = {
        'page_title': 'Top Engineering Disciplines & Courses',
        'header_title': 'Top Engineering Curriculums',
        'header_subtitle': 'Comprehensive academic curriculums designed to international engineering standards (Mechanical, Electrical, Civil, Robotics, Aerospace, Chemical, and Computer Systems).',
        'courses': courses,
        'categories': engineering_categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'enrolled_course_ids': enrolled_course_ids,
        'user_enrollments': user_enrollments,
        'is_engineering_view': True,
    }
    return render(request, 'courses/list.html', context)


def course_detail_view(request, slug):
    """Detailed course view with syllabus modules and enrollment CTA."""
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons__materials').select_related('category', 'instructor'),
        slug=slug
    )

    is_enrolled = False
    enrollment = None
    completed_lesson_ids = set()

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course, is_active=True).first()
        is_enrolled = enrollment is not None
        if is_enrolled:
            # Ensure progress is accurate upon viewing
            enrollment.recalculate_progress()
            completed_lesson_ids = set(
                LessonProgress.objects.filter(
                    student=request.user,
                    lesson__module__course=course,
                    completed=True
                ).values_list('lesson_id', flat=True)
            )

            next_lesson_to_study = None
            for mod in course.modules.all():
                for les in mod.lessons.all():
                    if les.id not in completed_lesson_ids:
                        next_lesson_to_study = les
                        break
                if next_lesson_to_study:
                    break
            if not next_lesson_to_study and course.modules.exists():
                first_mod = course.modules.first()
                if first_mod and first_mod.lessons.exists():
                    next_lesson_to_study = first_mod.lessons.first()

    context = {
        'page_title': course.title,
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids,
        'next_lesson_to_study': next_lesson_to_study if is_enrolled else None,
    }
    return render(request, 'courses/detail.html', context)


@login_required
def enroll_course_view(request, slug):
    """Enroll student in a course."""
    course = get_object_or_404(Course, slug=slug, is_published=True)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'progress_percent': 0, 'is_active': True}
    )

    if not created and not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save()

    # Recalculate to sync state
    enrollment.recalculate_progress()

    # Log activity
    LearningActivity.objects.create(
        student=request.user,
        activity_type='enrollment',
        description=f"Enrolled in course: {course.title}"
    )

    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('course_detail', slug=course.slug)


@login_required
def lesson_view(request, course_slug, lesson_id):
    """View lesson content, watch video, access materials, track progress."""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson.objects.select_related('module'), id=lesson_id, module__course=course)

    # Check if enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course, is_active=True).first()
    if not enrollment and not (request.user.is_staff or request.user == course.instructor):
        messages.warning(request, "Please enroll in this course to access lessons.")
        return redirect('course_detail', slug=course.slug)

    # Get or create lesson progress
    progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)

    # Get adjacent lessons for next/prev navigation
    all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))
    current_index = -1
    for idx, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = idx
            break

    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    # Materials
    materials = lesson.materials.all()

    # Module lessons with completion status
    completed_ids = set(
        LessonProgress.objects.filter(
            student=request.user,
            lesson__module__course=course,
            completed=True
        ).values_list('lesson_id', flat=True)
    )

    modules = course.modules.prefetch_related('lessons').all()

    # Update enrollment progress
    if enrollment:
        enrollment.recalculate_progress()

    context = {
        'page_title': f"{lesson.title} - {course.title}",
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'materials': materials,
        'modules': modules,
        'completed_ids': completed_ids,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'enrollment': enrollment,
    }
    return render(request, 'courses/lesson.html', context)


@login_required
def toggle_lesson_progress_view(request, lesson_id):
    """Toggle completed state of a lesson."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)

    progress.completed = not progress.completed
    progress.completed_at = timezone.now() if progress.completed else None
    progress.save()

    # Recalculate enrollment progress accurately
    enrollment = Enrollment.objects.filter(student=request.user, course=lesson.course).first()
    new_progress = 0
    if enrollment:
        new_progress = enrollment.recalculate_progress()

    if progress.completed:
        LearningActivity.objects.create(
            student=request.user,
            activity_type='lesson_completed',
            description=f"Completed lesson: {lesson.title}"
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json' or request.method == 'POST':
        return JsonResponse({
            'status': 'ok',
            'completed': progress.completed,
            'progress_percent': new_progress,
        })

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('lesson_view', course_slug=lesson.course.slug, lesson_id=lesson.id)


@login_required
def faculty_dashboard_view(request):
    """Faculty instructor dashboard."""
    user = request.user
    if not (user.profile.is_faculty or user.profile.is_admin or user.is_staff):
        messages.warning(request, "Access restricted to faculty members.")
        return redirect('student_dashboard')

    from assignments.models import Assignment, AssignmentSubmission
    from quizzes.models import Quiz

    taught_courses = Course.objects.filter(instructor=user).prefetch_related('modules__lessons', 'enrollments')
    total_students = Enrollment.objects.filter(course__instructor=user, is_active=True).values('student').distinct().count()

    assignments = Assignment.objects.filter(course__instructor=user)
    pending_submissions = AssignmentSubmission.objects.filter(
        assignment__course__instructor=user,
        status='submitted'
    ).select_related('student', 'assignment')[:5]

    quizzes = Quiz.objects.filter(course__instructor=user)

    context = {
        'page_title': 'Faculty Portal',
        'taught_courses': taught_courses,
        'total_courses': taught_courses.count(),
        'total_students': total_students,
        'assignments': assignments,
        'pending_submissions': pending_submissions,
        'pending_grading_count': pending_submissions.count(),
        'quizzes': quizzes,
    }
    return render(request, 'faculty/dashboard.html', context)


@login_required
def admin_dashboard_view(request):
    """Administrator portal overview."""
    user = request.user
    if not (user.profile.is_admin or user.is_staff or user.is_superuser):
        messages.error(request, "Administrator privileges required.")
        return redirect('student_dashboard')

    from django.contrib.auth.models import User
    from assignments.models import AssignmentSubmission
    from accounts.models import UserProfile

    total_students = UserProfile.objects.filter(role='student').count()
    total_faculty = UserProfile.objects.filter(role='faculty').count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_submissions = AssignmentSubmission.objects.count()

    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:8]
    recent_activities = LearningActivity.objects.select_related('student').order_by('-created_at')[:8]

    context = {
        'page_title': 'Admin Console',
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_submissions': total_submissions,
        'recent_users': recent_users,
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_dashboard/overview.html', context)
