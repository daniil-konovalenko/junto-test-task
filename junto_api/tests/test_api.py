from django.test import TestCase
from junto_api.models import User
from django.test import Client


class APITestCase(TestCase):
    @classmethod
    def setUpModule(cls):
        user = User.objects.create_user(username='test',
                                        password='SoPasswordMuchStrong',
                                        )

    
    def setUp(self):
        self.client = Client()
    
    def test_api_without_token(self):
        """Server should respond with 401 Authorization required
           to any request without API token """
        
        response = self.client.get('/api/', secure=True)
        self.assertEqual(response.status_code, 401)
    
    def test_get_token(self):
        """Server should respond with an API token
        to the request with correct credentials"""
        
        response = self.client.post('/auth',
                                    data={'username': 'test',
                                          'password': 'SoPasswordMuchStrong'})
        
        self.token = response.json().get('token')
        self.assertIsNotNone(self.token)
        headers = {'Authorization': f'Bearer {self.token}'}
        
        response = self.client.get('/menu', headers=headers)
        self.assertEqual(response.status_code, 200)
