from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.our_products, name='our_products'),
    path('add_category/', views.add_category, name='add_category'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about_us, name='about'),
    path('add_cart/', views.add_cart, name='add_cart'),
    path('all_payment/', views.all_payment, name='all_payment'),
    path('admin_base/', views.admin_base, name='admin_base'),
    # path('product-suggestions/', views.product_suggestions, name='product_suggestions'),
    path('payment/', views.payment, name='payment'), 
    path('list/', views.list, name='list'),
    path("contact-details/", views.contact_detail, name="contact_detail"),

]
