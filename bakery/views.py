
from django.contrib.auth import logout
from django.shortcuts import redirect,render
from django.conf import settings


def base(request):
    return render(request,'base.html')

def home(request):
    return render(request, "home.html")

def user_logout(request):
    logout(request)
    return redirect('base')

def about_as(request):
    return render(request,'about_as.html')

def our_products(request):
    return render(request,'our_products.html')
from django.shortcuts import render, redirect
from .models import Category, Product, Weight

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')  # Get the uploaded image
        weights = request.POST.getlist('weights[]')

        # Get or create category
        category, created = Category.objects.get_or_create(name=category_id)

        # Create product with image
        product = Product.objects.create(
            name=name,
            price=price,
            category=category,
            description=description,
            image=image  
        )

        # Create weights
        for weight_value in weights:
            if weight_value.strip():
                Weight.objects.create(product=product, weight_value=weight_value.strip())

        return redirect('our_products')  # Redirect after successful submission

    else:
        categories = Category.objects.values('name')
        return render(request, 'add_product.html', {'categories': categories})
# def our_products(request):
#     products = Product.objects.values('image','name','price')
#     return render(request, 'our_products.html', {'products': products, 'MEDIA_URL': settings.MEDIA_URL})
from django.conf import settings
from django.shortcuts import render
from .models import Product, Category

def our_products(request):
    category_id = request.GET.get('category')  # get from URL query param
    categories = Category.objects.values('id', 'name')  # as dictionaries

    if category_id:
        products = Product.objects.filter(category_id=category_id).values('image','name','price')
    else:
        products = Product.objects.values('image','name','price','category_id')

    return render(request, 'our_products.html', {
        'categories': categories,
        'products': products,
        'MEDIA_URL': settings.MEDIA_URL,
        'selected_category': int(category_id) if category_id else None
    })
