from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # TEst createing a new user wiuth an email is successful
        email = "test@example.com"
        password = "TestPass1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        # TEst that the email for a new user is normalized

        email = "test@EXAMPLE.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Tests that a user with no email rasies error

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test1234')

    def test_create_new_super_user(self):
        # Test creating a new super user
        user = get_user_model().objects.create_superuser(
            "testAdmin@example.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
