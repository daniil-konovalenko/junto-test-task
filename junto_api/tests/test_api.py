from django.test import TestCase
from junto_api.models import User, Category, Dish
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
    
    def test_access_api_with_incorrect_token(self):
        headers = {'HTTP_AUTHORIZATION': 'Bearer obviously wrong token'}
        response = self.client.get('/api/menu', **headers)
        self.assertEqual(response.status_code, 403)
    
    def test_refresh_token(self):
        response = self.client.post('/api/auth',
                                    data={'username': 'test',
                                          'password': 'SoPasswordMuchStrong'})
        refresh_token = response.json().get('refresh', {}).get('token')
        
        response = self.client.post('/api/auth/refresh',
                                    data={'token': refresh_token})
        self.assertEqual(response.status_code, 200)
        
        # Now we should be able to access API with the new token
        new_access_token = response.json().get('access', {}).get('token')
        headers = {'HTTP_AUTHORIZATION': f'Bearer {new_access_token}'}
        response = self.client.get('/api/menu', **headers)
        self.assertEqual(response.status_code, 200)
        
        # We also have to check that the old refresh token is no longer valid
        response = self.client.post('/api/auth/refresh',
                                    data={'token': refresh_token})
        self.assertEqual(response.status_code, 403)
    
    def test_menu(self):
        # Prepare some food to fill the menu
        food = Category.objects.create(name='Еда')
        sauces = Category.objects.create(name='Соусы')
        burgers = Category.objects.create(name='Бургеры')
        
        cheeseburger = Dish.objects.create(name='Чизбургер', price='50.00')
        fries = Dish.objects.create(name='Картофель фри', price='49.99')
        schezwan_sauce = Dish.objects.create(name='Сычуанский соус',
                                             price='100500')
        
        food.subcategories.add(burgers)
        food.dishes.add(fries)
        burgers.dishes.add(cheeseburger)
        sauces.dishes.add(schezwan_sauce)
        
        food.save()
        sauces.save()
        burgers.save()
        cheeseburger.save()
        fries.save()
        schezwan_sauce.save()
        
        response = self.client.post('/api/auth',
                                    data={'username': 'test',
                                          'password': 'SoPasswordMuchStrong'})
        
        self.access_token = response.json().get('access', {}).get('token')
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.get('/api/menu', **headers)
        
        self.assertEqual(response.status_code, 200)
        
        expected_json = {
            'categories': {
                'count': 2,
                'items': [
                    {
                        'name': 'Еда',
                        'subcategories': {
                            'count': 1,
                            'items': [
                                {
                                    'name': 'Бургеры',
                                    'dishes': {
                                        'count': 1,
                                        'items': [
                                            {
                                                'id': 1,
                                                'name': 'Чизбургер',
                                                'price': '50.00'
                                            }
                                        ]
                                    },
                                    'subcategories': {
                                        'count': 0,
                                        'items': []
                                    }
                                }
                            ]},
                        'dishes': {
                            'count': 1,
                            'items': [
                                {
                                    'id': 2,
                                    'name': 'Картофель фри',
                                    'price': '49.99',
                                }
                            ]}
                    },
                    {
                        'name': 'Соусы',
                        'subcategories': {
                            'count': 0,
                            'items': []
                        },
                        'dishes': {
                            'count': 1,
                            'items': [
                                {
                                    'id': 3,
                                    'name': 'Сычуанский соус',
                                    'price': '100500.00'
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        self.assertDictEqual(expected_json, response.json())
