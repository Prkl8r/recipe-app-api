from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    # Test the publicly available ingredients API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required for retreiving ingredients
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    # Test private ingredients API so ingredients can be retrieved by authenticated clients

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com",
            "testPass"
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        # Test retrieving a list of IngredientSerializer.

        # Arrange
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Chicken")

        # Act
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        # Assert
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # Test that ingredients for the authenticated user are returned.
        # Arrange
        user2 = get_user_model().objects.create_user(
            "other@example.com",
            "testPAssword"
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        # Act
        res = self.client.get(INGREDIENTS_URL)

        # Assert
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_success(self):
        # Test that the user is able to create a new ingredient.
        # Arrange
        payload = {"name": "Bacon"}
        self.client.post(INGREDIENTS_URL, payload)

        # ACT
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        # Assert
        self.assertTrue(exists)

    def test_create_ingredient_invalid_name(self):
        # Test creating a new ingredient with an invalid name
        # Arrange
        payload = {"name": ""}

        # Act
        res = self.client.post(INGREDIENTS_URL, payload)

        # ASSERT
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        # Test filtering ingredients by those assigned to recipes
        ingredient1 = Ingredient.objects.create(user=self.user, name="Tortilla")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Black Beans")
        recipe = Recipe.objects.create(
            title='Breakfast Burrito',
            time_minutes=23,
            price=16,
            user=self.user
        )

        recipe.ingredients.add(ingredient1)

        # Act
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        # Assert
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_ingredients_assigned_to_recipes_are_unique(self):
        # Test filtering ingredients by assigned recipes returns unique values
        # Arrange
        ingredient = Ingredient.objects.create(user=self.user, name="Sausage")
        Ingredient.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title='Breakfast Burrito',
            time_minutes=25,
            price=15.75,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Buttermilk Pancakes and Sausage',
            time_minutes=23,
            price=3,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        # Act
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        # Assert
        self.assertEqual(len(res.data), 1)
