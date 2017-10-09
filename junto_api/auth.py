from django.contrib.auth.models import User
import jwt
import datetime
from django.http import HttpRequest
from django.http import HttpResponse


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
        auth_header =  request.META.get('HTTP_AUTHORIZATION')
        print(request.META)
        print(auth_header)
        if auth_header is not None:
            
            return function(request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    return wrap