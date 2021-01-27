from django.contrib.auth import get_user_model
from core.models import Recipe, Tag, Ingredient


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


def sample_recipe(user, **params):
    """
    Create and return a sample recipe
    """
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 5,
        'price': 5.00,
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name='Main Course'):
    """
    Create and return a sample tag
    """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Salt'):
    """
    Create and return a sample ingredient
    """
    return Ingredient.objects.create(user=user, name=name)
