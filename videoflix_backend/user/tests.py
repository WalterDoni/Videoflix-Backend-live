from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core import mail
import json
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token

User = get_user_model()

class UserViewsTests(TestCase):
    def setUp(self):
        # Create a test user for use in the tests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_signup_view(self):
       url = reverse('signup')
       data = {
           'email': 'newuser@example.com',
           'password': 'newpassword',
           'username': 'newuser'
       }
       # Post data to the signup endpoint
       response = self.client.post(url, json.dumps(data), content_type='application/json')
       self.assertEqual(response.status_code, 201)  # Check if the status code is 201 (Created)
       self.assertIn('message', response.json())  # Ensure the response contains a 'message' key
       self.assertEqual(User.objects.count(), 2)  # Ensure a new user has been created

       # Check whether an e-mail has been sent
       self.assertEqual(len(mail.outbox), 1)
       self.assertIn('Bestätigungsmail', mail.outbox[0].subject)  # Verify the actual subject of the sent email

    def test_login_view(self):
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        # Post data to the login endpoint
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Check if the status code is 200 (OK)
        self.assertIn('token', response.json())  # Ensure the response contains a 'token' key

    def test_delete_user_view(self):
        url = reverse('user-delete', kwargs={'pk': self.user.pk})
        # Send a DELETE request to the user delete endpoint
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)  # Check if the status code is 200 (OK)
        self.assertEqual(User.objects.count(), 0)  # Ensure the user has been deleted

    def test_change_user_values_view(self):
        url = reverse('user-update', kwargs={'pk': self.user.pk})
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        # Send a PATCH request to update user details
        response = self.client.patch(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Check if the status code is 200 (OK)
        self.user.refresh_from_db()  # Refresh user data from the database
        self.assertEqual(self.user.username, 'updateduser')  # Verify the username was updated
        self.assertEqual(self.user.email, 'updated@example.com')  # Verify the email was updated

    def test_get_username_and_email_by_urlid(self):
        url = reverse('user-username', kwargs={'pk': self.user.pk})
        # Send a GET request to fetch username and email by user ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Check if the status code is 200 (OK)
        data = response.json()  # Parse the JSON response
        self.assertEqual(data['username'], 'testuser')  # Verify the username in the response
        self.assertEqual(data['email'], 'test@example.com')  # Verify the email in the response

    def test_send_email(self):
        url = reverse('send-email')
        data = {
            'email': 'sender@example.com',
            'name': 'Sender',
            'title': 'Test Email',
            'message': 'This is a test email.'
        }
        # Send a POST request to the send email endpoint
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Check if the status code is 200 (OK)
        self.assertIn('message', response.json())  # Ensure the response contains a 'message' key
        self.assertEqual(len(mail.outbox), 1)  # Check if one email has been sent
        self.assertEqual(mail.outbox[0].subject, 'Test Email')  # Verify the subject of the sent email

    def test_verify_email_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        url = reverse('verify-email-confirm', kwargs={'uidb64': uid, 'token': token})
        # Send a GET request to the email confirmation endpoint
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Check if the status code is 302 (Redirect)
        self.assertEqual(User.objects.get(pk=self.user.pk).email_is_verified, True)  # Verify the email is marked as verified

    def test_verify_email_complete_view(self):
        url = reverse('verify-email-complete')
        # Send a GET request to the email verification complete endpoint
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Check if the status code is 302 (Redirect)