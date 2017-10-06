from django.contrib import admin
from .models import Category, Dish, Restaurant, Order, DishOrder


class CategoryInline(admin.TabularInline):
    model = Category
    verbose_name = 'Subcategory'
    verbose_name_plural = 'Subcategories'


class DishInline(admin.TabularInline):
    model = Category.dishes.through
    verbose_name = 'Dish'
    verbose_name_plural = 'Dishes'


class DishOrderInline(DishInline):
    model = DishOrder
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
    ]


class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'restaurant', 'operator', 'status', 'total']
    inlines = [
        DishOrderInline,
    ]

class OrderInline(admin.TabularInline):
    model = Order
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы"


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']
    inlines = [
        OrderInline
    ]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Order, OrderAdmin)
