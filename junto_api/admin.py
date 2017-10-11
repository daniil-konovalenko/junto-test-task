from django.contrib import admin
from .models import Category, Dish, Restaurant, Order, DishOrder


class CategoryInline(admin.TabularInline):
    model = Category
    verbose_name = 'подкатегория'
    verbose_name_plural = 'подкатегории'


class DishInline(admin.TabularInline):
    model = Category.dishes.through
    verbose_name = 'блюдо'
    verbose_name_plural = 'блюда'


class DishOrderInline(DishInline):
    model = DishOrder
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
        DishInline
    ]


class DishAdmin(admin.ModelAdmin):
    def get_categories(self, obj):
        return ', '.join(cat.name for cat in obj.categories.all())
    
    get_categories.short_description = 'категории'
    list_display = ['name', 'get_categories', 'price']


def make_paid(modeladmin, request, queryset):
    queryset.update(status=Order.PAID)


make_paid.short_description = "Отметить выделенные заказы как оплаченные"


def make_cancelled(modeladmin, request, queryset):
    queryset.update(status=Order.CANCELLED)


make_cancelled.short_description = "Отметить выделенные заказы как отменённые"


class OrderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'restaurant', 'operator', 'status', 'total']
    inlines = [
        DishOrderInline,
    ]
    actions = [make_paid, make_cancelled]


class OrderInline(admin.TabularInline):
    model = Order
    verbose_name = "заказ"
    verbose_name_plural = "заказы"


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Order, OrderAdmin)
