<<<<<<< Updated upstream

from django.contrib.auth import logout
from django.shortcuts import redirect,render
from django.conf import settings


def base(request):
    return render(request,'base.html')
from django.conf import settings


def base(request):
    return render(request,'base.html')
=======
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .utils.zerobounce import verify_email_with_zerobounce
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Category, Product, Weight

CustomUser = get_user_model()

def base(request):
    return render(request, "base.html")
>>>>>>> Stashed changes

def home(request):
    return render(request, "home.html")

<<<<<<< Updated upstream
def user_logout(request):
    logout(request)
    return redirect('base')

=======
>>>>>>> Stashed changes
def about_as(request):
    return render(request,'about_as.html')

def our_products(request):
    return render(request,'our_products.html')
<<<<<<< Updated upstream
from django.shortcuts import render, redirect
from .models import Category, Product, Weight
=======

def register(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()

    print("Registering email:", email)
    #  ZeroBounce validation
    import json

    result = verify_email_with_zerobounce(email)
    if isinstance(result, str):
        result = json.loads(result)

    if not result or result.get("status") != "valid":
        return JsonResponse({"success": False, "message": "Invalid email. Please enter a real Gmail address."})

    #  Check duplicate email
    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already exists"})

    #  Check duplicate username
    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already exists"})

    #  Create user safely
    try:
        user = CustomUser.objects.create_user(
            username=username,
            email=email,    
            password=password,
            phone=phone,
            address=address
        )
    except IntegrityError as e:
        return JsonResponse({"success": False, "message": f"Registration failed: {str(e)}"})

    return JsonResponse({
        "success": True,
        "message": "Registration successful! Please login."
    })

@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                auth_login(request, auth_user)
                return JsonResponse({"success": True, "message": "Login successful"})
            else:
                return JsonResponse({"success": False, "message": "Invalid password"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})

@csrf_exempt
def logout(request):
    auth_logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully"})
>>>>>>> Stashed changes

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
