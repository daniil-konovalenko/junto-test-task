import datetime
import jwt
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='название')
    supercategory = models.ForeignKey('self',
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      blank=True,
                                      related_name='subcategories',
                                      related_query_name='subcategory')
    
    def serialize(self):
        return {
            'name': self.name,
            'dishes': {
                'count': self.dishes.count(),
                'items': [dish.serialize() for dish in self.dishes.all()]
            },
            'subcategories': {
                'count': self.subcategories.count(),
                'items': [cat.serialize() for cat in self.subcategories.all()]
            }
        }

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name='название')
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                verbose_name='стоимость, ₽')
    categories = models.ManyToManyField(Category,
                                        related_name='dishes',
                                        related_query_name='dish',
                                        verbose_name='категории')
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': str(self.price)
        }
    
    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'блюда'

    def __str__(self):
        return f'{self.name} ({self.price} ₽)'


class Restaurant(models.Model):
    name = models.CharField(max_length=200, verbose_name='название')
    city = models.CharField(max_length=50, verbose_name='город')
    
    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'
        
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city
        }
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    operator = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='orders',
                                 related_query_name='order',
                                 verbose_name='оператор')
    
    PENDING = 0
    PAID = 1
    CANCELLED = 2
    STATUS_CHOICES = (
        (PENDING, 'Ожидает оплаты'),
        (PAID, 'Оплачен'),
        (CANCELLED, 'Отменён'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                      default=PENDING,
                                      verbose_name='статус')
    
    restaurant = models.ForeignKey(Restaurant,
                                   on_delete=models.CASCADE,
                                   related_name='order',
                                   related_query_name='orders',
                                   verbose_name='ресторан')
    
    dishes = models.ManyToManyField(Dish, through='DishOrder')
    
    created_at = models.DateTimeField(editable=False,
                                      verbose_name='время создания')
    updated_at = models.DateTimeField()
    
    @property
    def total(self) -> Decimal:
        return sum([rel.current_price for rel in self.dishorder_set.all()])
    total.fget.short_description = 'сумма, ₽'
    
    def save(self, *args, **kwargs):
        """Update timestamps on save"""
        if self.id is None:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
    
    def __str__(self):
        return f'Заказ №{self.id}'


class DishOrder(models.Model):
    """Due to  price changes we need to """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE,
                             verbose_name='блюдо')
    current_price = models.DecimalField(max_digits=8,
                                        decimal_places=2,
                                        verbose_name='стоимость на момент заказа, ₽')
    
    def __str__(self):
        return str(self.dish)


class RefreshToken(models.Model):
    value = models.CharField(max_length=500, db_index=True)
    revoked = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='refresh_tokens',
                             related_query_name='refresh_token')
    @classmethod
    def create_token(cls, user: User,
                     expires: datetime.datetime,
                     secret: str) -> 'RefreshToken':
        payload = {
            'type': 'refresh',
            'user_id': user.id,
            'exp': expires
        }
        token_value: str = jwt.encode(payload, secret).decode()
        token = cls.objects.create(value=token_value, user=user)
        return token
    
    def validate(self):
        try:
            payload = jwt.decode(self.value, key=settings.SECRET_KEY)
            return not self.revoked and payload.get('type') == 'refresh'
        
        except jwt.DecodeError:
            return False
        except jwt.ExpiredSignatureError:
            return False
        
    def __str__(self):
        return f'token #{self.id}'
