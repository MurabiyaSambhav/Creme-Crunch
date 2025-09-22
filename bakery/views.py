from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from django.conf import settings
from .models import BakeryCategory, BakerySubCategory, Product, Weight, ContactForm, ProductImages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
import re, json

CustomUser = get_user_model()

# ----------------------------
# Base & Home
# ----------------------------
def base(request):
    return render(request, "base.html")

def home(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)  
    return render(request, "home.html", {"categories": categories})

# ----------------------------
# User Auth
# ----------------------------
def register(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()

    if not re.match(r"^[A-Za-z]{3,60}$", username):
        return JsonResponse({"success": False, "message": "Invalid username."})
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email):
        return JsonResponse({"success": False, "message": "Invalid email."})
    if not re.match(r"^\d{10}$", phone):
        return JsonResponse({"success": False, "message": "Phone must be 10 digits."})

    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already exists"})
    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already exists"})

    try:
        CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone, address=address)
    except IntegrityError as e:
        return JsonResponse({"success": False, "message": f"Registration failed: {str(e)}"})

    return JsonResponse({"success": True, "message": "Registration successful! Please login."})

# ----------------------------
# Login & Logout
# ----------------------------

def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(email=email)
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                auth_login(request, auth_user)
                redirect_url = reverse("home")
                if auth_user.is_staff:
                    redirect_url = reverse("admin_base")
                return JsonResponse({"success": True, "message": "Login successful", "redirect_url": redirect_url})
            else:
                return JsonResponse({"success": False, "message": "Invalid password"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

def logout(request):
    auth_logout(request)
    return redirect("home")

# ----------------------------
# Product Management
# ----------------------------
def add_product(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_ids = request.POST.getlist("subcategories")
        weights = request.POST.getlist("weights[]")
        prices = request.POST.getlist("weight_prices[]")
        images = request.FILES.getlist("images[]")
        main_index = int(request.POST.get("main_image", 0))

        # Create product
        if hasattr(Product, "category"):  # Product has category FK
            category = BakeryCategory.objects.get(id=category_id)
            product = Product.objects.create(
                name=name,
                description=description,
                category=category
            )
        else:
            product = Product.objects.create(
                name=name,
                description=description
            )

        if hasattr(product, "subcategories"):
            product.subcategories.set(subcategory_ids)

        # Add weights
        for w, p in zip(weights, prices):
            if w.strip() and p.strip():
                Weight.objects.create(product=product, weight=w.strip(), price=p)

        # Add images
        for idx, img in enumerate(images):
            ProductImages.objects.create(
                product=product,
                image=img,
                is_main=(idx == main_index)
            )

        return redirect("our_products")

    return render(request, "admin/add_product.html", {"categories": categories})


# ----------------------------
# All Products
# ----------------------------

def our_products(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    products = Product.objects.all().prefetch_related('images', 'weights')

    # Add a main_image attribute for the template
    for product in products:
        main_image = product.images.filter(is_main=True).first()
        product.main_image = main_image

    return render(request, "our_products.html", {
        "categories": categories,
        "products": products,
        "MEDIA_URL": settings.MEDIA_URL
    })

# ----------------------------
# Categories & Subcategories
# ----------------------------
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")
        subcategories = request.POST.getlist("subcategories[]")
        category, created = BakeryCategory.objects.get_or_create(category_name=category_name)
        for sub in subcategories:
            if sub.strip():
                BakerySubCategory.objects.get_or_create(category=category, subcategory_name=sub.strip())
        return redirect("add_category")
    return render(request, "admin/add_category.html", {"categories": BakeryCategory.objects.all()})

def get_subcategories(request, category_id):
    subs = BakerySubCategory.objects.filter(category_id=category_id)
    sub_list = [{"id": sub.id, "name": sub.subcategory_name} for sub in subs]
    return JsonResponse({"subcategories": sub_list})

# ----------------------------
# Contact & About
# ----------------------------
def contact(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    return render(request, 'contact.html', {'categories': categories})

# ----------------------------
# About Us
# ----------------------------

def about_us(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        if len(message) <= 180:
            ContactForm.objects.create(name=name, email=email, phone=phone, message=message)
            return redirect('about_us')
    return render(request, 'about_us.html', {'categories': categories})

# ----------------------------
# Add to Cart
# ----------------------------

def add_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get('product_id')
        weight_id = data.get('weight_id')
        quantity = int(data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        # TODO: Add to cart logic
        return JsonResponse({'status': 'success', 'message': 'Product added to cart'})

    # GET request: show product page
    product_id = request.GET.get('product_id')
    if not product_id:
        return redirect('home')

    try:
        product = Product.objects.prefetch_related('weights', 'images').get(id=product_id)
        main_image = product.images.filter(is_main=True).first()

        # Get all categories for selection (optional)
        categories = BakeryCategory.objects.all()

        # Get first weight (for default price)
        first_weight = product.weights.first()
    except Product.DoesNotExist:
        return redirect('home')

    return render(request, 'add_cart.html', {
        'product': product,
        'main_image': main_image,
        'categories': categories,
        'first_weight': first_weight
    })

# ----------------------------
# Payment
# ----------------------------

def payment(request):
    return render(request, 'payment.html')

def admin_base(request):
    return render(request, 'admin/admin_base.html')

def all_payment(request):
    return render(request, 'admin/all_payment.html')
