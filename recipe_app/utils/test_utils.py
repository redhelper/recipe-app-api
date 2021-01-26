from django.contrib.auth import get_user_model


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_user(
        email='test@rafacorp.com',
        password='test1234!',
        name="Test boi"):
    """
    Creates a sample user
    """
    return get_user_model().objects.create_user(email, password)
