from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=15, help_text='Time limit in minutes (0 for untimed)')
    pass_score = models.FloatField(default=60.0, help_text='Passing percentage (e.g. 60.0)')
    max_attempts = models.PositiveIntegerField(default=3)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all()) or 0


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text='Question text or prompt')
    explanation = models.TextField(blank=True, help_text='Explanation shown after submission')
    order = models.PositiveIntegerField(default=1)
    points = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'quiz_question_options'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(default=0.0)
    score_percent = models.FloatField(default=0.0)
    is_passed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score_percent}%)"

    def calculate_score(self):
        """Calculate and save score based on answers."""
        total_points = self.quiz.total_points
        if total_points == 0:
            self.score = 0
            self.score_percent = 0
            self.is_passed = True
            self.is_completed = True
            self.save()
            return

        earned_points = 0
        for answer in self.answers.select_related('selected_option', 'question'):
            if answer.selected_option and answer.selected_option.is_correct:
                earned_points += answer.question.points

        self.score = earned_points
        self.score_percent = round((earned_points / total_points) * 100, 1)
        self.is_passed = self.score_percent >= self.quiz.pass_score
        self.is_completed = True
        self.submitted_at = timezone.now()
        self.save()


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'quiz_answers'
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Attempt {self.attempt_id} - Q{self.question_id}"
