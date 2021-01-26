from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from utils.test_utils import create_user
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """
    Test the public tags API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving tags
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """
    Test the authenticated user, tags API
    """

    def setUp(self):
        self.user = create_user(
            email='test@rafacorp.com',
            password='superpass123!',
            name='yea boiiiii',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_tags(self):
        """
        Test retrieving a list of tags
        """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_tags_for_only_current_user(self):
        """
        Tags returned must be for the current user
        """
        user2 = create_user(
            email='test2@rafacorp.com',
            password='superpass456!',
            name='aww yeaaaaa',
        )
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def create_tag_successful(self):
        """
        Test creating a new tag
        """
        payload = {
            'name': 'Test Tag',
        }
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """
        Test creating a tag with invalid payload
        """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
