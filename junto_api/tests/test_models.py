from django.test import TestCase
from junto_api.models import Category, Dish

# Create your tests here.
class CategoryTestCase(TestCase):
    def setUp(self):
        self.fastfood = Category.objects.create(name='Фастфуд')
        self.burgers = Category.objects.create(name='Бургеры')
        self.beef_burgers = Category.objects.create(name='Бургеры из говядины')
        
        self.fastfood.save()
        self.burgers.save()
        self.beef_burgers.save()
        
        self.fastfood.subcategories.add(self.burgers)
        self.burgers.subcategories.add(self.beef_burgers)
        
    def test_subcategories(self):
        self.assertTrue(self.burgers in self.fastfood.subcategories.all())
        self.assertTrue(self.beef_burgers in self.burgers.subcategories.all())
    
    def test_supercategories(self):
        self.assertTrue(self.burgers.supercategory is self.fastfood)
        self.assertTrue(self.beef_burgers.supercategory is self.burgers)

    def test_dish_relation(self):
        texas_burger = Dish(name='Техасский бургер', price=250)
        fries = Dish(name='Картофель фри', price=50)
        
        texas_burger.save()
        fries.save()
        
        self.beef_burgers.dishes.add(texas_burger)
        self.fastfood.dishes.add(fries)
        
        self.assertTrue(texas_burger in self.beef_burgers.dishes.all())
        self.assertTrue(fries in self.fastfood.dishes.all())
        