from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'auth/refresh', views.refresh, name='refresh'),
    url(r'auth', views.get_token, name='auth'),
    url(r'menu', views.menu, name='menu'),
    url(r'order', views.new_order),
    url(r'restaurants', views.restaurants, name='restaurants')
]
