from django.test import TestCase, Client
from django.urls import reverse

from utils.test_utils import sample_user, sample_superuser


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = sample_superuser()
        self.client.force_login(self.admin)
        self.user = sample_user()

    def test_users_listed(self):
        """
        Test that users are listed on user page
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
        Test that the user edit page works
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
