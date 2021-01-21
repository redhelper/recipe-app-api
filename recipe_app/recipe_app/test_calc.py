from django.test import TestCase

from recipe_app.calc import add


class CalcTests(TestCase):
    def test_add_numbers(self):
        """
        Two numbers must be added together
        """
        X = 2
        Y = 4
        res = add(X, Y)
        self.assertEqual(res, 6)
