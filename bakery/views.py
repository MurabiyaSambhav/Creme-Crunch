from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
import re, json
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Product, Weight, ContactForm

CustomUser = get_user_model()


# ----------------------------
# Base & Home
# ----------------------------
def base(request):
    return render(request, "base.html")

def home(request):
    return render(request, "home.html")


# ----------------------------
# Register
# ----------------------------
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
        return JsonResponse({"success": False, "message": "Invalid username. Only letters allowed (3-60 chars)."})

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

    return JsonResponse({
        "success": True,
        "message": "Registration successful! Please login."
    })


# ----------------------------
# Login / Logout
# ----------------------------
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
                        "redirect_url": reverse("admin_home")
                    })
                else:
                    return JsonResponse({
                        "success": True,
                        "message": "Login successful",
                        "redirect_url": reverse("home")
                    })
            else:
                return JsonResponse({"success": False, "message": "Invalid password"})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


def logout(request):
    auth_logout(request)
    return redirect("home")


# ----------------------------
# Add Product
# ----------------------------
def add_product(request):
    categories = Category.objects.filter(parent__isnull=True)  # only main categories

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        subcategory_ids = request.POST.getlist("subcategories")  #  multiple checkboxes
        description = request.POST.get("description")
        image = request.FILES.get("image")
        weights = request.POST.getlist("weights[]")

        category = Category.objects.get(id=category_id)

        product = Product.objects.create(
            name=name,
            price=price,
            category=category,
            image=image,
            description=description,
        )

        #  Save many-to-many subcategories
        if subcategory_ids:
            product.subcategories.set(subcategory_ids)

        #  Save weights
        for w in weights:
            if w.strip():
                Weight.objects.create(product=product, weight=w.strip())

        return redirect("our_products")  # change to your product list URL

    return render(request, "admin/add_product.html", {"categories": categories})


# ----------------------------
# Product List (with category filter)
# ----------------------------
def our_products(request):
    category_id = request.GET.get('category')
    categories = Category.objects.filter(parent__isnull=True).values('id', 'name')

    if category_id:
        products = Product.objects.filter(category_id=category_id).values('image', 'name', 'price')
    else:
        products = Product.objects.values('image', 'name', 'price', 'category_id')

    return render(request, 'our_products.html', {
        'categories': categories,
        'products': products,
        'MEDIA_URL': settings.MEDIA_URL,
        'selected_category': int(category_id) if category_id else None
    })


# ----------------------------
# Category APIs (AJAX)
# ----------------------------
def get_categories(request):
    categories = list(Category.objects.filter(parent__isnull=True).values('id', 'name'))
    return JsonResponse({"categories": categories})

def get_subcategories(request, category_id):
    subcategories = list(Category.objects.filter(parent_id=category_id).values('id', 'name'))
    return JsonResponse({"subcategories": subcategories})

def add_category(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            if not name:
                return JsonResponse({"success": False, "error": "Name required."})

            if Category.objects.filter(name__iexact=name, parent__isnull=True).exists():
                return JsonResponse({"success": False, "error": "Category already exists."})

            Category.objects.create(name=name)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request."})

def add_subcategory(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            parent_id = data.get("parent")

            if not parent_id or not name:
                return JsonResponse({"success": False, "error": "Parent and name required."})

            parent = Category.objects.filter(id=parent_id, parent__isnull=True).first()
            if not parent:
                return JsonResponse({"success": False, "error": "Parent category not found."})

            if Category.objects.filter(name__iexact=name, parent=parent).exists():
                return JsonResponse({"success": False, "error": "Subcategory already exists."})

            Category.objects.create(name=name, parent=parent)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request."})


# ----------------------------
# Other Pages
# ----------------------------
def about_us(request):
    error_message = ""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        if len(message) > 180:
            error_message = "Message cannot exceed 180 characters."
        else:
            ContactForm.objects.create(name=name, email=email, phone=phone, message=message)
            return redirect('about_us')
    return render(request, 'about_us.html', {'error_message': error_message})

def admin_home(request):
    return render(request, 'admin/admin_home.html')

def all_payment(request):
    return render(request, 'admin/all_payment.html')

def contact(request):
    return render(request, 'contact.html')
