
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
# from .utils.zerobounce import verify_email_with_zerobounce
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Category, Product, Weight
import re

CustomUser = get_user_model()

def base(request):
    return render(request, "base.html")

def home(request):
    return render(request, "home.html")


# def register(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request"})

#     username = request.POST.get("username", "").strip()
#     email = request.POST.get("email", "").strip().lower()
#     password = request.POST.get("password")
#     phone = request.POST.get("phone", "").strip()
#     address = request.POST.get("address", "").strip()

#     print("Registering email:", email)

#     #  ZeroBounce validation
#     result = verify_email_with_zerobounce(email)
#     print("ZeroBounce raw result:", result)

#     if not isinstance(result, dict):
#         return JsonResponse({"success": False, "message": "Error verifying email with ZeroBounce."})

#     if "error" in result:  # API key / credits issue
#         return JsonResponse({
#             "success": False,
#             "message": f"ZeroBounce error: {result['error']}"
#         })

#     status = result.get("status", "").lower()
#     if status != "valid":
#         return JsonResponse({
#             "success": False,
#             "message": f"Invalid email. ZeroBounce returned status: {status or 'missing'}"
#         })

#     #  Check duplicate email
#     if CustomUser.objects.filter(email=email).exists():
#         return JsonResponse({"success": False, "message": "Email already exists"})

#     #  Check duplicate username
#     if CustomUser.objects.filter(username=username).exists():
#         return JsonResponse({"success": False, "message": "Username already exists"})

#     #  Create user safely
#     try:
#         CustomUser.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             phone=phone,
#             address=address
#         )
#     except IntegrityError as e:
#         return JsonResponse({"success": False, "message": f"Registration failed: {str(e)}"})

#     return JsonResponse({
#         "success": True,
#         "message": "Registration successful! Please login."
#     })

def register(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()

    # --- Regex validation ---
    if not re.match(r"^[A-Za-z]{3,60}$", username):
        return JsonResponse({"success": False, "message": "Invalid username. Only letters allowed (3-20 chars)."})

    if not re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email):
        return JsonResponse({"success": False, "message": "Invalid email address."})

    if not re.match(r"^\d{10}$", phone):  
        return JsonResponse({"success": False, "message": "Phone must be 10 digits."})

    # --- Duplicate checks ---
    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already exists"})
    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already exists"})

    # --- Create user safely ---
    try:
        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )
    except IntegrityError as e:
        return JsonResponse({"success": False, "message": f"Registration failed: {str(e)}"})

    #  Return success → handled in JS to show on login form
    return JsonResponse({
        "success": True,
        "message": "Registration successful! Please login."
    })

def login(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                auth_login(request, auth_user)

                if auth_user.is_staff:
                    return JsonResponse({
                        "success": True,
                        "message": "Staff login successful",
                        "redirect_url": "templates/admin/admin_home/"
                    })
                else:
                    return JsonResponse({
                        "success": True,
                        "message": "Login successful",
                        "redirect_url": "/"
                    })
            else:
                return JsonResponse({"success": False, "message": "Invalid password"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


def logout(request):
    auth_logout(request)
    return redirect("home")

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
        return render(request, 'admin/add_product.html', {'categories': categories})

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


def about_as(request):
    return render(request,'about_as.html')

def our_products(request):
    return render(request,'our_products.html')

def admin_home(request):
    return render(request,'admin/admin_home.html')

def all_payment(request):
    return render(request,'admin/all_payment.html')