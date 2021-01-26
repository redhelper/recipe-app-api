from django.contrib.auth import get_user_model


def sample_superuser(**params):
    """
    Creates a sample superuser
    """
    defaults = {
        'email': "admin@rafacorp.com",
        'password': "superadminpass123!",
    }
    defaults.update(**params)
    return get_user_model().objects.create_superuser(**defaults)


def sample_user(**params):
    """
    Creates a sample user
    """
    defaults = {
        'email': 'test@rafacorp.com',
        'password': 'test1234!',
        'name': "Test boi",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)
