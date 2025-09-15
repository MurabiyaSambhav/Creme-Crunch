
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('our_products/', views.our_products, name='our_products'),
    path('about/', views.about_as, name='about'),
    path('add/', views.add_product, name='add'),



    

]
