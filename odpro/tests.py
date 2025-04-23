from django.contrib.auth import get_user, get_user_model
from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class LoginTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'test@test.net'
        self.password = 'testpass123'
        tester = get_user_model()
        tester.objects.create_user(email=self.email, password=self.password)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertTrue('_auth_user_id' in self.client.session)


    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': self.email,
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Login page reloaded
        self.assertContains(response, "Please enter a correct email and password")

    def test_login_required_page(self):
        response = self.client.get('/odprofile/', follow=True)
        self.assertEqual(response.request['PATH_INFO'], reverse('login'))
