from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import RefreshToken
from datetime import datetime, timedelta
from typing import Union
from .auth import token_required, generate_access_token


@token_required
def menu(request: HttpRequest) -> Union[JsonResponse, HttpResponse]:
    return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_POST
def get_token(request: HttpRequest) -> Union[JsonResponse, HttpResponse]:
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    user = authenticate(username=username, password=password)
    
    if user is not None:
        now = datetime.utcnow()
        
        access_token_expires = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION_TIME)
        
        access_token = generate_access_token(user,
                                             access_token_expires,
                                             secret=settings.SECRET_KEY)
        
        refresh_token_expires = now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION_TIME)
        
        refresh_token = RefreshToken.create_token(user, refresh_token_expires,
                                                  settings.SECRET_KEY)
        refresh_token.save()
        
        return JsonResponse({
            'access': {
                'token': access_token,
                'expires_in': settings.ACCESS_TOKEN_EXPIRATION_TIME
            },
            'refresh': {
                'token': refresh_token.value,
                'expires_in': settings.REFRESH_TOKEN_EXPIRATION_TIME
            }
        })
    
    else:
        return HttpResponse('Unauthorized', status=401)

