from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = "testing@rafacorp.com"
        password = "supersecurePassword!123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_with_lowercase_email(self):
        """
        Test creating a new user with an email has lowercase enforced
        """
        email = "testing@RafaCorP.com"
        user = get_user_model().objects.create_user(
            email=email,
            password="supersecurePassword!123",
        )
        self.assertEqual(user.email, email.lower())

    def test_user_with_no_email(self):
        """
        Test creating a new user with no email fails
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password="supersecurePassword!123",
            )

    def test_create_new_superuser(self):
        """
        Test creating a new superuser works
        """
        user = get_user_model().objects.create_superuser(
            email="testing@rafacorp.com",
            password="supersecurePassword!123",
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
