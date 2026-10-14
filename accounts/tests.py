from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile


class AccountsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='teststudent@smartlearn.com',
            email='teststudent@smartlearn.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )

    def test_user_profile_auto_created(self):
        """Test UserProfile signal creates profile automatically."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'student')
        self.assertTrue(self.user.profile.is_student)
        self.assertFalse(self.user.profile.is_faculty)

    def test_user_initials(self):
        """Test user initials generation."""
        self.assertEqual(self.user.profile.initials, 'JD')

    def test_role_property(self):
        """Test changing role updates properties."""
        self.user.profile.role = 'faculty'
        self.user.profile.save()
        self.assertTrue(self.user.profile.is_faculty)
        self.assertFalse(self.user.profile.is_student)
