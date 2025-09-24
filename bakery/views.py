from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from django.conf import settings
from .models import BakeryCategory, BakerySubCategory, Product, Weight, ContactForm, ProductImages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
import re, json

import re
from django.contrib import messages


CustomUser = get_user_model()

# ----------------------------
# Base & Home
# ----------------------------
def base(request):
    return render(request, "base.html")

def home(request):
    categories = BakeryCategory.objects.all()
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
    categories = BakeryCategory.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_ids = request.POST.getlist("subcategories")  # <-- multiple subcategories now
        weights = request.POST.getlist("weights[]")
        prices = request.POST.getlist("prices[]")
        images = request.FILES.getlist("images[]")
        main_index = int(request.POST.get("main_image", 0))

        # Create product with category
        product = Product.objects.create(
            name=name,
            description=description,
            category_id=category_id if category_id else None,
        )

        # Add subcategories (ManyToMany)
        if subcategory_ids:
            subcategories = BakerySubCategory.objects.filter(id__in=subcategory_ids)
            product.subcategories.set(subcategories)

        # Add weights
        for w, p in zip(weights, prices):
            if w.strip() and str(p).strip():
                Weight.objects.create(
                    product=product,
                    weight=w.strip(),
                    price=float(p.strip())
                )

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
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")
    sort_option = request.GET.get("sort")

    categories = BakeryCategory.objects.all()
    subcategories = BakerySubCategory.objects.all()
    products = Product.objects.all()

    selected_category = None
    selected_subcategory = None
    parent_category = None

    # Filter by subcategory first (ManyToMany)
    if subcategory_id:
        try:
            selected_subcategory = BakerySubCategory.objects.get(id=subcategory_id)
            parent_category = selected_subcategory.category.id
            products = products.filter(subcategories=selected_subcategory).distinct()
        except BakerySubCategory.DoesNotExist:
            selected_subcategory = None

    # Filter by category only if no subcategory is selected
    elif category_id:
        try:
            selected_category = BakeryCategory.objects.get(id=category_id)
            parent_category = selected_category.id
            products = products.filter(category=selected_category)
        except BakeryCategory.DoesNotExist:
            selected_category = None

    # Search
    if query:
        products = products.filter(name__icontains=query)

    # Sorting
    if sort_option == "price_low":
        products = products.order_by("weights__price")
    elif sort_option == "price_high":
        products = products.order_by("-weights__price")
    elif sort_option == "latest":
        products = products.order_by("-id")
    elif sort_option == "popularity":
        # Implement your popularity logic here if needed
        pass
    elif sort_option == "rating":
        # Implement your rating logic here if needed
        pass

    # Pagination
    paginator = Paginator(products.distinct(), 9)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    # Attach main image & first weight for each product
    for p in products_page:
        p.main_image = p.images.filter(is_main=True).first()
        p.first_weight = p.weights.first()

    context = {
        "categories": categories,
        "subcategories": subcategories,
        "products": products_page,
        "selected_category": selected_category,
        "selected_subcategory": selected_subcategory,
        "parent_category": parent_category,
        "query": query,
        "page_range": get_page_range(paginator, products_page.number),
        "total_results": products.count(),
        "start_index": products_page.start_index(),
        "end_index": products_page.end_index(),
    }

    return render(request, "our_products.html", context)


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
    categories = BakeryCategory.objects.all()
    success = False
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        if len(message) <= 180:
            ContactForm.objects.create(name=name, email=email, phone=phone, message=message)
            return JsonResponse({"success": True, "message": "Thank you for contacting us, we will be in touch shortly."})
        else:
            return JsonResponse({"success": False, "message": "Message too long."})
    return render(request, 'about_us.html', {'categories': categories, 'success': success})

def contact_detail(request):
    contacts = ContactForm.objects.values("id", "name", "email", "phone", "message", "submitted_at", "created_at", "updated_at").order_by("-submitted_at")
    return render(request, 'admin/contact_details.html', {"contacts": contacts})

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

# ----------------------------
# Pagination Helper
# ----------------------------

def get_page_range(paginator, current_page, max_pages=5):
    """
    Custom pagination numbers with ellipsis.
    Example: 1 ... 3 4 5 ... 10
    """
    total_pages = paginator.num_pages
    if total_pages <= max_pages:
        return range(1, total_pages + 1)

    page_range = []

    # Always show first page
    page_range.append(1)

    # Add left dots
    if current_page > 3:
        page_range.append("...")

    # Pages around current page
    start = max(2, current_page - 1)
    end = min(total_pages - 1, current_page + 1)
    page_range.extend(range(start, end + 1))

    # Add right dots
    if current_page < total_pages - 2:
        page_range.append("...")

    # Always show last page
    page_range.append(total_pages)

    return page_range

# ----------------------------
# Product Suggestions (AJAX) 
# ----------------------------

def product_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        # Search in product names or category names
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__category_name__icontains=query)
        ).distinct()[:10]  # limit suggestions to 10

        for product in products:
            suggestions.append({
                'id': product.id,
                'name': product.name,
                'category': product.category.category_name if product.category else ''
            })

    return JsonResponse({'results': suggestions})



def admin_base(request):
    return render(request, 'admin/admin_base.html')

def all_payment(request):
    return render(request, 'admin/all_payment.html')

# ----------------------------
# Contact 
# ----------------------------
def contact(request):
    categories = BakeryCategory.objects.all()
    return render(request, "contact.html", {"categories": categories})

def list(request):
    products = Product.objects.all().prefetch_related('weights', 'images')
    categories = BakeryCategory.objects.prefetch_related('subcategories')

    return render(request, 'admin/master_list.html',{'products': products,'categories': categories,})





