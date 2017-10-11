from typing import Optional
from django.conf import settings
from django.contrib.auth.models import User
import jwt
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import JsonResponse
from django.contrib.auth import authenticate

from junto_api.models import RefreshToken


def generate_access_token(user: User,
                          expires: datetime,
                          secret: str) -> str:
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': expires,
        },
        key=secret,
        algorithm='HS256').decode()
    
    return token


def token_required(function):
    def wrap(request: HttpRequest, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header is not None:
            # Assuming that header looks like this: 'Bearer token'
            _, token, *_ = auth_header.split()
            
            user = authenticate(request, token=token)
            if user is not None:
                request.user = user
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied()
        else:
            return JsonResponse({'error': 'No token provided'},
                                status=401)
    
    return wrap


def generate_tokens(user: User):
    now = datetime.utcnow()
    
    access_token_expires = now + timedelta(
        seconds=settings.ACCESS_TOKEN_EXPIRATION_TIME)
    
    access_token = generate_access_token(user,
                                         access_token_expires,
                                         secret=settings.SECRET_KEY)
    
    refresh_token_expires = now + timedelta(
        seconds=settings.REFRESH_TOKEN_EXPIRATION_TIME)
    
    refresh_token = RefreshToken.create_token(user, refresh_token_expires,
                                              settings.SECRET_KEY)
    refresh_token.save()
    
    return {
        'access': {
            'token': access_token,
            'expires_in': settings.ACCESS_TOKEN_EXPIRATION_TIME
        },
        'refresh': {
            'token': refresh_token.value,
            'expires_in': settings.REFRESH_TOKEN_EXPIRATION_TIME
        }
    }


class AccessTokenAuthBackend(object):
    def authenticate(self, request, token: str = None) -> Optional[User]:
        try:
            payload = jwt.decode(token, key=settings.SECRET_KEY)
            user_id = payload.get('user_id')
            return self.get_user(user_id)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.DecodeError:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None