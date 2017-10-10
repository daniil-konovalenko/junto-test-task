from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'auth', views.get_token, name='auth'),
    url(r'menu', views.menu, name='menu'),
    
]
