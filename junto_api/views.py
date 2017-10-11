import jwt
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import RefreshToken, Order, Restaurant, Dish, DishOrder
from typing import Union
from .auth import token_required, generate_tokens
from .models import Category
import json


@token_required
def menu(request: HttpRequest) -> JsonResponse:
    top_level_categories = Category.objects.filter(supercategory=None)
    
    return JsonResponse({
        'categories': {
            'count': len(top_level_categories),
            'items': [cat.serialize() for cat in top_level_categories]
        }
    })


@token_required
@csrf_exempt
@require_POST
def new_order(request: HttpRequest) -> JsonResponse:
    try:
        order_data = json.loads(request.body.decode())
        
        dish_ids = order_data.get('dish_ids')
        if not isinstance(dish_ids, list):
            return JsonResponse({'error': 'dish_ids should be a list'},
                                status=400)
        
        restaurant_id = order_data.get('restaurant_id')
        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            return JsonResponse({'error': f'Restaurant with id {restaurant_id}'
                                          'does not exist'},
                                status=400)
        
        order = Order.objects.create(restaurant=restaurant,
                                     operator=request.user)
        order.save()
        
        failed = []
        
        for dish_id in dish_ids:
            try:
                dish = Dish.objects.get(pk=int(dish_id))
                relation = DishOrder.objects.create(dish=dish,
                                                    order=order,
                                                    current_price=dish.price)
                relation.save()
            except (Dish.DoesNotExist, ValueError):
                failed.append(dish_id)
        
        return JsonResponse({
            'order_id': order.id,
            'failed_dishes_ids': failed
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format'},
                            status=400)
    
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
