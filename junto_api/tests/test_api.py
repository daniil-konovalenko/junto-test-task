from django.test import TestCase
from junto_api.models import User
from django.test import Client
from django.test.utils import override_settings
import time


class APITestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test',
                                        password='SoPasswordMuchStrong',
                                        )
        user.save()
        self.client = Client()
    
    def test_access_api_without_a_token(self):
        response = self.client.get('/api/menu')
        self.assertEqual(response.status_code, 401)
    
    def test_get_auth_instead_of_post(self):
        """GET on /api/auth should return Method Not Allowed"""
        response = self.client.get('/api/auth')
        self.assertEqual(response.status_code, 405)
    
    def test_get_token_and_access_api(self):
        """
        Server should respond with an API token
        to the request with correct credentials"
        """
        
        response = self.client.post('/api/auth',
                                    data={'username': 'test',
                                          'password': 'SoPasswordMuchStrong'})
        
        self.assertEqual(response.status_code, 200)
        self.access_token = response.json().get('access', {}).get('token')
        self.refresh_token = response.json().get('refresh', {}).get('token')
        self.assertIsNotNone(self.access_token)
        self.assertIsNotNone(self.refresh_token)
        
        # Not that we got the access token and the refresh token
        # we should be able to access api methods
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.get('/api/menu', **headers)
        self.assertEqual(response.status_code, 200)
    
    def test_get_token_with_incorrect_credentials(self):
        """
        If there is no such user in database,
        api/auth should respond with 403 Forbidden
        """
        response = self.client.post('/api/auth',
                                    data={
                                        'username': 'test',
                                        'password': 'so wrong'
                                    })
        self.assertEqual(response.status_code, 401)
    
    def test_get_token_without_credentials(self):
        response = self.client.post('/api/auth')
        self.assertEqual(response.status_code, 401)

    @override_settings(ACCESS_TOKEN_EXPIRATION_TIME=2)
    def test_expired_token(self):
        response = self.client.post('/api/auth',
                                    data={'username': 'test',
                                          'password': 'SoPasswordMuchStrong'})
        
        self.assertEqual(response.status_code, 200)
        access_token = response.json().get('access', {}).get('token')
        # Wait for token to expire
        time.sleep(3)
        # Try to access a protected endpoint
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        response = self.client.get('/api/menu', **headers)
        self.assertEqual(response.status_code, 403)
        
        error = response.json().get('error')
        self.assertIsNotNone(error)
        self.assertIn('expired', error)
        
    def access_api_with_incorrect_token(self):
        headers = {'HTTP_AUTHORIZATION': 'Bearer obviously wrong token'}
        response = self.client.get('/api/menu', **headers)
        self.assertEqual(response.status_code, 401)
        error = response.json().get('error')
        self.assertIn('invalid token', error.lower())
