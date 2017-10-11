import jwt
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import RefreshToken
from typing import Union
from .auth import token_required, generate_tokens
from .models import Category


@token_required
def menu(request: HttpRequest) -> Union[JsonResponse, HttpResponse]:
    top_level_categories = Category.objects.filter(supercategory=None)
    
    return JsonResponse({
        'categories': {
            'count': len(top_level_categories),
            'items': [cat.serialize() for cat in top_level_categories]
        }
    })


@csrf_exempt
@require_POST
def get_token(request: HttpRequest) -> Union[JsonResponse, HttpResponse]:
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    user = authenticate(username=username, password=password)
    
    if user is not None:
        tokens = generate_tokens(user)
        return JsonResponse(tokens)
    
    else:
        return HttpResponse('Unauthorized', status=401)


@csrf_exempt
@require_POST
def refresh(request: HttpRequest) -> JsonResponse:
    token = request.POST.get('token')
    
    if token is not None:
        try:
            payload = jwt.decode(token, key=settings.SECRET_KEY)
            if payload.get('type') != 'refresh':
                raise ValueError('Incorrect token type')
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)
            token_object = (RefreshToken.objects.all()
                                                .filter(value=token)
                                                .first())
            
            if token_object in user.refresh_tokens.all() and not token_object.revoked:
                # Revoke all previous refresh tokens
                for token in user.refresh_tokens.all():
                    token.revoked = True
                    token.save()
                tokens = generate_tokens(user)
                return JsonResponse(tokens)
            else:
                return JsonResponse({'error': 'Refresh token is revoked '
                                              'or invalid. Please obtain'
                                              'a new pair of tokens via '
                                              'username/password authentication'},
                                    status=403)
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Refresh token expired. '
                                          'Please obtain a new pair of tokens '
                                          'via username/password authentication'},
                                status=403)
        except (jwt.DecodeError, RefreshToken.DoesNotExist):
            return JsonResponse({'error': 'Invalid refresh token.'
                                          'Please obtain a new pair of tokens '
                                          'via username/password authentication'},
                                status=401)
        except ValueError:
            return JsonResponse({'error': 'Invalid token type. '
                                          'Please make sure that you are '
                                          'sending the refresh token'},
                                status=401)
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'User corresponding to the token '
                                          'does not exist. Please contact '
                                          'the administrator to resolve '
                                          'this issue'},
                                status=401)
