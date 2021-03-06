from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from utils.test_utils import sample_user

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


class PublicUserAPITests(TestCase):
    """
    Test the users API (Public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            'email': 'test@rafacorp.com',
            'password': 'superpass123!',
            'name': 'yea boiiiii',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_existing_user(self):
        """
        Test creating a duplicate fails
        """
        payload = {
            'email': 'test@rafacorp.com',
            'password': 'superpass123!',
            'name': 'yea boiiiii',
        }
        sample_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test checking that password is longer than 5 characters
        """
        payload = {
            'email': 'test@rafacorp.com',
            'password': 'pp!',
            'name': 'ya boi',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test that a token is created for the user
        """
        payload = {
            'email': 'test@rafacorp.com',
            'password': 'superpass123!',
        }
        sample_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        sample_user(email='test@rafacorp.com', password='superpass!')
        payload = {
            'email': 'test@rafacorp.com',
            'password': 'superpass123!',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        res = self.client.post(
            TOKEN_URL,
            {
                'email': 'test@rafacorp.com',
                'password': 'superpass123!',
            },
        )

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required
        """
        res = self.client.post(
            TOKEN_URL,
            {
                'email': 'test',
                'password': '',
            },
        )
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test that authentication is required for users
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """
    Test the users API (Logged In)
    """

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in used
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                'name': self.user.name,
                'email': self.user.email,
            },
        )

    def test_post_to_me_not_allowed(self):
        """
        Test that POST requests to the /me endpoint are not allowed
        """
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_update_user_profile(self):
        """
        Updating user profile as authenticated user
        """
        payload = {
            'name': 'new boiiiii',
            'password': 'newpass123!',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
