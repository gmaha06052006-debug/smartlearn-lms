from django.test import TestCase
from django.contrib.auth.models import User
from courses.models import CourseCategory, Course
from quizzes.models import Quiz, Question, QuestionOption, QuizAttempt, QuizAnswer


class QuizzesTestCase(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='inst@test.com', password='pwd')
        self.student = User.objects.create_user(username='stud@test.com', password='pwd')
        self.cat = CourseCategory.objects.create(name='AI')
        self.course = Course.objects.create(title='AI Intro', category=self.cat, instructor=self.instructor)

        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Intro Quiz',
            pass_score=60.0,
            created_by=self.instructor
        )
        self.q1 = Question.objects.create(quiz=self.quiz, text='What is 2+2?', points=5)
        self.opt_correct = QuestionOption.objects.create(question=self.q1, text='4', is_correct=True)
        self.opt_wrong = QuestionOption.objects.create(question=self.q1, text='5', is_correct=False)

    def test_quiz_scoring_calculation(self):
        """Test automatic score calculation on quiz submission."""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, student=self.student)
        QuizAnswer.objects.create(attempt=attempt, question=self.q1, selected_option=self.opt_correct)
        attempt.calculate_score()

        self.assertEqual(attempt.score, 5)
        self.assertEqual(attempt.score_percent, 100.0)
        self.assertTrue(attempt.is_passed)
        self.assertTrue(attempt.is_completed)
