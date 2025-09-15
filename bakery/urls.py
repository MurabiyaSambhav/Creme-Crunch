from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('our_products/', views.our_products, name='our_products'),
    path('about/', views.about_as, name='about'),
    path('add/', views.add_product, name='add'),
    path('', views.base, name='base'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'), 
    path('logout/', views.logout, name='logout'), 
]
