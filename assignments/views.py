from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment
from analytics.models import LearningActivity
from .models import Assignment, AssignmentSubmission
from .forms import AssignmentSubmissionForm, AssignmentCreateForm, AssignmentGradeForm


@login_required
def assignment_list_view(request):
    """List assignments relevant to the user."""
    user = request.user
    role = user.profile.role if hasattr(user, 'profile') else 'student'

    if role == 'faculty':
        assignments = Assignment.objects.filter(course__instructor=user).select_related('course')
    elif role == 'admin':
        assignments = Assignment.objects.all().select_related('course')
    else:
        enrolled_course_ids = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)
        assignments = Assignment.objects.filter(course_id__in=enrolled_course_ids).select_related('course')

    # Get student's submission status for each assignment
    user_submissions = {}
    if role == 'student':
        submissions = AssignmentSubmission.objects.filter(student=user, assignment__in=assignments)
        user_submissions = {s.assignment_id: s for s in submissions}

    context = {
        'page_title': 'Assignments',
        'assignments': assignments,
        'user_submissions': user_submissions,
        'now': timezone.now(),
    }
    return render(request, 'assignments/list.html', context)


@login_required
def assignment_detail_view(request, pk):
    """View assignment details and handle submission."""
    assignment = get_object_or_404(Assignment.objects.select_related('course', 'created_by'), pk=pk)
    user = request.user
    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=user).first()

    form = None
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = user
            sub.submitted_at = timezone.now()
            sub.status = 'submitted'
            sub.save()

            LearningActivity.objects.create(
                student=user,
                activity_type='assignment_submit',
                description=f"Submitted assignment: {assignment.title}"
            )
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentSubmissionForm(instance=submission)

    # If faculty, fetch all submissions for this assignment
    all_submissions = []
    if user.profile.role in ['faculty', 'admin'] or user == assignment.course.instructor:
        all_submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')

    context = {
        'page_title': assignment.title,
        'assignment': assignment,
        'submission': submission,
        'form': form,
        'all_submissions': all_submissions,
    }
    return render(request, 'assignments/detail.html', context)


@login_required
def assignment_create_view(request):
    """Faculty creates new assignment."""
    if not (request.user.profile.is_faculty or request.user.profile.is_admin or request.user.is_staff):
        messages.error(request, 'Permission denied.')
        return redirect('assignment_list')

    if request.method == 'POST':
        form = AssignmentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('assignment_list')
    else:
        form = AssignmentCreateForm()
        # Filter courses to those taught by current user if faculty
        if request.user.profile.is_faculty:
            form.fields['course'].queryset = Course.objects.filter(instructor=request.user)

    context = {
        'page_title': 'Create Assignment',
        'form': form,
    }
    return render(request, 'assignments/create.html', context)


@login_required
def assignment_grade_view(request, submission_id):
    """Faculty grades student submission."""
    submission = get_object_or_404(AssignmentSubmission.objects.select_related('assignment', 'student'), pk=submission_id)
    assignment = submission.assignment

    if not (request.user.profile.is_faculty or request.user.profile.is_admin or request.user == assignment.course.instructor):
        messages.error(request, 'Permission denied.')
        return redirect('assignment_list')

    if request.method == 'POST':
        form = AssignmentGradeForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.graded_by = request.user
            sub.graded_at = timezone.now()
            sub.status = 'graded'
            sub.save()
            messages.success(request, f'Grade saved for {submission.student.get_full_name()}!')
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentGradeForm(instance=submission)

    context = {
        'page_title': f"Grade: {submission.student.get_full_name()}",
        'submission': submission,
        'assignment': assignment,
        'form': form,
    }
    return render(request, 'assignments/grade.html', context)
