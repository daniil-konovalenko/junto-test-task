from django.conf import settings
from django.contrib.auth.models import User
import jwt
import datetime
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse


def generate_access_token(user: User,
                          expires: datetime.datetime,
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
            _, token = auth_header.split()
            
            try:
                payload = jwt.decode(token, key=settings.SECRET_KEY)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Signature expired. '
                                              'Renew your token '
                                              'using your '
                                              'refresh token'},
                                    status=403)
            except jwt.DecodeError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            return function(request, *args, **kwargs)
        else:
            return HttpResponse({'error': 'No token provided'},
                                status=401)
    return wrap
