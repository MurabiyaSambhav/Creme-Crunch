
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('base/', views.base, name='base'),
    path('our_products/', views.our_products, name='our_products'),
    path('about/', views.about_us, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'), 
    path('logout/', views.logout, name='logout'), 
    path('contact/', views.contact, name='contact'), 
    path('admin_home/', views.admin_home, name='admin_home'),
    path('our_products/', views.our_products, name='our_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('get_categories/', views.get_categories, name='get_categories'),
    path('get_subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('all_payment/', views.all_payment, name='all_payment'),
]
