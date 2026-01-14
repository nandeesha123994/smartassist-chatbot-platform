from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

class SuccessMessageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }

    def test_registration_success_message(self):
        response = self.client.post(self.register_url, self.user_data, follow=True)
        messages = list(get_messages(response.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Registration successful! Welcome to ChatAI.")

    def test_login_success_message(self):
        # First register the user
        User.objects.create_user(username='testuser', password='testpassword123')
        
        # Then login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, follow=True)
        
        messages = list(get_messages(response.request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Login successful! Welcome back.")
