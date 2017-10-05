from django.contrib import admin
from .models import Category, Dish
# Register your models here.


class CategoryInline(admin.TabularInline):
    model = Category
    verbose_name = 'Subcategory'
    verbose_name_plural = 'Subcategories'
    

class DishInline(admin.TabularInline):
    model = Category.dishes.through
    verbose_name = 'Dish'
    verbose_name_plural = 'Dishes'


class CategoryDishInline(admin.TabularInline):
    model = Dish.categories.through
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
        DishInline
    ]
    
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
