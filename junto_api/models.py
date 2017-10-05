from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    supercategory = models.ForeignKey('self',
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      blank=True,
                                      related_name='subcategories',
                                      related_query_name='subcategory')

    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                verbose_name='Стоимость, ')
    categories = models.ManyToManyField(Category,
                                        related_name='dishes',
                                        related_query_name='dish',
                                        verbose_name='Категории')
    
    class Meta:
        verbose_name_plural = 'Dishes'

    def __str__(self):
        return f'{self.name} ({self.price} ₽)'


class Restaurant(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    city = models.CharField(max_length=50, verbose_name='Город')
    
    def __str__(self):
        return self.name
