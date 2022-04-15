from django.test import TestCase, \
    Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password1234"
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password1234567",
            name="Test User full name"
        )

    def test_users_listed(self):
        # Test users are listed on the user page
        url = reverse("admin:core_user_changeList")
        res = self.client.get(url)

        # Looks for a 200 and that the output can find the expected contents
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
