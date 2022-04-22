from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    # Test the publically available tags API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required for retrieving tags
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    # Test the authorized user tags API

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'password12345',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        # Test retreive tags
        Tag.objects.create(user=self.user, name='Pork')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # Tests that tags returned are for the authenticated user
        user2 = get_user_model().objects.create_user(
            "other@example.com",
            "password1234",
        )
        Tag.objects.create(user=user2, name='Chicken')
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        # Test creating a new tag
        payload = {"name": "Test Tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid_name(self):
        # Test creating a new tag with inv
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retreive_tags_assigned_to_recipes(self):
        # Test filtering tags by those assigned to recipes
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Chicken")
        recipe = Recipe.objects.create(
            title='Chicken Pot Pie',
            time_minutes=93,
            price=17,
            user=self.user
        )
        recipe.tags.add(tag2)

        # Act
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)  # Breakfast Tag
        serializer2 = TagSerializer(tag2)  # Chicken Tag

        # Assert
        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_filtered_tags_assigned_to_recipes_are_unique(self):
        # Test filtering tags by assigned returns unique values
        # Arrange
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title='Breakfast Burrito',
            time_minutes=93,
            price=17,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Buttermilk Pancakes',
            time_minutes=23,
            price=3,
            user=self.user
        )

        recipe1.tags.add(tag)  # Add 'Breakfast' tag to 'Breakfast Burrito'
        recipe2.tags.add(tag)  # Add 'Breakfast' tag to 'Buttermilk PAncakes'

        # Act
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Assert
        self.assertEqual(len(res.data), 1)
