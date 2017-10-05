from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    supercategory = models.ForeignKey('self',
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      related_name='subcategories',
                                      related_query_name='subcategory')

    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name
