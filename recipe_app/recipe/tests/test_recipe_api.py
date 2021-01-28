
import tempfile
import os
from PIL import Image

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from utils.test_utils import (
    sample_user,
    sample_recipe,
    sample_ingredient,
    sample_tag,
)
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def IMAGE_UPLOAD_URL(recipe_id):
    """
    Return an uploaded recipe image url
    """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def DETAIL_URL(recipe_id):
    """
    Return a recipe detail url
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeAPITests(TestCase):
    """
    Test Unauthenticated Recipe Api Access
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving recipes
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """
    Test the authenticated user, recipes API
    """

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_recipes(self):
        """
        Test retrieving a list of recipes
        """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_recipes_only_for_current_user(self):
        """
        Recipes returned must be for the current user
        """
        user2 = sample_user(email="test2@rafacorp.com")
        sample_recipe(user=user2)
        recipe = sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = DETAIL_URL(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
        Test creating a recipe
        """
        payload = {
            'title': 'Chocolate Cheesecake',
            'time_minutes': 30,
            'price': 5.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        Test creating a recipe with tags
        """
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Lime Cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
        Test creating a recipe with ingredients
        """
        ing1 = sample_ingredient(user=self.user, name='Salt')
        ing2 = sample_ingredient(user=self.user, name='Pork')
        payload = {
            'title': 'Meaty Lovers Pizza',
            'ingredients': [ing1.id, ing2.id],
            'time_minutes': 60,
            'price': 15.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ing1, ingredients)
        self.assertIn(ing2, ingredients)

    def test_partial_update_recipe(self):
        """
        Test updating recipe with PATCH
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Spaghetti Carbonara',
            'tags': [new_tag.id],
        }
        res = self.client.patch(DETAIL_URL(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """
        Test updating recipe with PUT
        """
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_ing = sample_ingredient(user=self.user, name='Spaghetti')

        payload = {
            'title': 'Spaghetti with Mushroom Sauce',
            'ingredients': [new_ing.id],
            'time_minutes': 30,
            'price': '20.00'
        }
        res = self.client.put(DETAIL_URL(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)
        self.assertIn(new_ing, ingredients)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
        Test uploading an image to recipe
        """
        url = IMAGE_UPLOAD_URL(self.recipe.id)

        # create a temporal empty file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # create a sample image
            img = Image.new('RGB', (10, 10))
            # save it into the file
            img.save(ntf, format='JPEG')
            # set the file pointer back to it's beginning
            ntf.seek(0)

            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        Test uploading an invalid image
        """
        url = IMAGE_UPLOAD_URL(self.recipe.id)
        res = self.client.post(
            url, {'image': 'somethingelse'},
            format='multipart',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
