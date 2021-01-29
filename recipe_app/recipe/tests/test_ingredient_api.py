from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from utils.test_utils import sample_user, sample_ingredient, sample_recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITests(TestCase):
    """
    Test the public ingredients API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving ingredients
        """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """
    Test the authenticated user, ingredients API
    """

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_ingredients(self):
        """
        Test retrieving a list of ingredients
        """
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Flour')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_ingredients_only_for_current_user(self):
        """
        Ingredients returned must be for the current user
        """
        user2 = sample_user(
            email='test2@rafacorp.com',
            password='superpass456!',
            name='aww yeaaaaa',
        )
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Flour')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def create_ingredient_successful(self):
        """
        Test creating a new ingredient
        """
        payload = {
            'name': 'Test Ingredient',
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """
        Test creating an ingredient with invalid payload
        """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """
        Test filtering ingredients by those assigned to recipes
        """
        ingredient1 = sample_ingredient(user=self.user, name='Apples')
        ingredient2 = sample_ingredient(user=self.user, name='Turkey')
        recipe = sample_recipe(
            user=self.user,
            title='Apple Crumble',
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """
        Test that resulting ingredient list does not contain repeated values
        """
        ingredient = sample_ingredient(user=self.user, name='Eggs')
        sample_ingredient(user=self.user, name='Cheese')
        recipe1 = sample_recipe(
            user=self.user,
            title='Eggs Benedict',
        )
        recipe2 = sample_recipe(
            user=self.user,
            title='Coriander Eggs on Toast',
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
