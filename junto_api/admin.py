from django.contrib import admin
from .models import Category
# Register your models here.


class CategoryInline(admin.TabularInline):
    model = Category
    verbose_name = 'Subcategory'
    verbose_name_plural = 'Subcategories'
    
    
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CategoryInline,
    ]

admin.site.register(Category, CategoryAdmin)
