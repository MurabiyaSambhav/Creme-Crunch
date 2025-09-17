from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # only one empty string path
    path('home/', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('our_products/', views.our_products, name='our_products'),
    path('about/', views.about_as, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'), 
    path('logout/', views.logout, name='logout'), 
    path("admin_home/", views.admin_home, name="admin_home"),
    path('add_product/', views.add_product, name='add_product'),
    path('all_payment/', views.all_payment, name='all_payment'),
]
