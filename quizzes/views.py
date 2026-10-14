from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment
from analytics.models import LearningActivity
from .models import Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer


@login_required
def quiz_list_view(request):
    """List quizzes accessible to the user."""
    user = request.user
    role = user.profile.role if hasattr(user, 'profile') else 'student'

    if role == 'faculty':
        quizzes = Quiz.objects.filter(course__instructor=user).select_related('course')
    elif role == 'admin':
        quizzes = Quiz.objects.all().select_related('course')
    else:
        enrolled_course_ids = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)
        quizzes = Quiz.objects.filter(course_id__in=enrolled_course_ids, is_published=True).select_related('course')

    # Get user attempts for each quiz
    attempts_by_quiz = {}
    if role == 'student':
        for q in quizzes:
            attempts = QuizAttempt.objects.filter(student=user, quiz=q, is_completed=True).order_by('-score_percent')
            attempts_by_quiz[q.id] = {
                'count': attempts.count(),
                'best_score': attempts.first().score_percent if attempts.exists() else None,
                'passed': attempts.filter(is_passed=True).exists(),
            }

    context = {
        'page_title': 'Quizzes & Tests',
        'quizzes': quizzes,
        'attempts_by_quiz': attempts_by_quiz,
    }
    return render(request, 'quizzes/list.html', context)


@login_required
def quiz_start_view(request, pk):
    """Start a new quiz attempt or resume active one."""
    quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__options'), pk=pk)
    user = request.user

    # Check attempt limit
    completed_attempts = QuizAttempt.objects.filter(quiz=quiz, student=user, is_completed=True).count()
    if completed_attempts >= quiz.max_attempts and not request.user.is_staff:
        messages.warning(request, f"You have reached the maximum allowed attempts ({quiz.max_attempts}) for this quiz.")
        return redirect('quiz_list')

    # Find incomplete attempt or create new
    attempt = QuizAttempt.objects.filter(quiz=quiz, student=user, is_completed=False).first()
    if not attempt:
        attempt = QuizAttempt.objects.create(quiz=quiz, student=user)

    return redirect('quiz_take', attempt_id=attempt.id)


@login_required
def quiz_take_view(request, attempt_id):
    """Take the quiz with questions and countdown timer."""
    attempt = get_object_or_404(QuizAttempt.objects.select_related('quiz', 'student'), id=attempt_id, student=request.user)

    if attempt.is_completed:
        return redirect('quiz_result', attempt_id=attempt.id)

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related('options').all()

    # Calculate remaining time if timed
    remaining_seconds = 0
    if quiz.duration_minutes > 0:
        elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
        total_allowed_seconds = quiz.duration_minutes * 60
        remaining_seconds = max(0, int(total_allowed_seconds - elapsed_seconds))

        if remaining_seconds <= 0:
            # Auto-submit if time expired
            attempt.calculate_score()
            messages.info(request, "Time expired! Your quiz was submitted automatically.")
            return redirect('quiz_result', attempt_id=attempt.id)

    # Saved answers map
    saved_answers = {a.question_id: a.selected_option_id for a in attempt.answers.all()}

    context = {
        'page_title': quiz.title,
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'remaining_seconds': remaining_seconds,
        'saved_answers': saved_answers,
    }
    return render(request, 'quizzes/take.html', context)


@login_required
def quiz_submit_view(request, attempt_id):
    """Submit quiz and calculate score."""
    attempt = get_object_or_404(QuizAttempt.objects.select_related('quiz'), id=attempt_id, student=request.user)

    if attempt.is_completed:
        return redirect('quiz_result', attempt_id=attempt.id)

    if request.method == 'POST':
        quiz = attempt.quiz
        for question in quiz.questions.all():
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                option = QuestionOption.objects.filter(id=option_id, question=question).first()
                QuizAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_option': option}
                )

        attempt.calculate_score()

        LearningActivity.objects.create(
            student=request.user,
            activity_type='quiz_attempt',
            description=f"Completed quiz: {quiz.title} ({attempt.score_percent}%)"
        )

        messages.success(request, f"Quiz submitted! You scored {attempt.score_percent}%.")
        return redirect('quiz_result', attempt_id=attempt.id)

    return redirect('quiz_take', attempt_id=attempt.id)


@login_required
def quiz_result_view(request, attempt_id):
    """View quiz result breakdown with correct answers and explanations."""
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'student'),
        id=attempt_id
    )

    if attempt.student != request.user and not (request.user.profile.is_faculty or request.user.profile.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('quiz_list')

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related('options').all()
    user_answers = {a.question_id: a.selected_option_id for a in attempt.answers.all()}

    context = {
        'page_title': f"Result: {quiz.title}",
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'user_answers': user_answers,
    }
    return render(request, 'quizzes/result.html', context)
