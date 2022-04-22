from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@example.com", password="testpassword"):
    # Create a sample user
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # TEst creating a new user with an email is successful
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
        # Tests that a user with no email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test1234')

    def test_new_superuser(self):
        # Test creating a new super user
        user = get_user_model().objects.create_superuser(
            "testAdmin@example.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        # Test tag string representation
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Test the ingredient string representation
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Test recipe string creation.
        # Arrange
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=5.00
        )

        # Assert
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        # Test that image is saved in the correct location
        # Arrange
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        # Act
        exp_path = f'uploads/recipe/{uuid}.jpg'

        # Assert
        self.assertEqual(file_path, exp_path)
