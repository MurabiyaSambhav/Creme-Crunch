from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import BakeryCategory, BakerySubCategory, Product, Weight, ContactForm, ProductImages
from django.core.paginator import Paginator
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
        prices = request.POST.getlist("prices[]")
        images = request.FILES.getlist("images[]")

        product = Product.objects.create(name=name, description=description)

        # Add weights
        for w, p in zip(weights, prices):
            if w.strip() and p.strip():
                Weight.objects.create(product=product, weight=w.strip(), price=p.strip())

        # Add images
        for img in images:
            ProductImages.objects.create(product=product, image=img)

        return redirect("our_products")

    return render(request, "admin/add_product.html", {"categories": categories})



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


def get_subcategories(request, category_id):
    subs = BakerySubCategory.objects.filter(category_id=category_id)
    sub_list = [{"id": sub.id, "name": sub.subcategory_name} for sub in subs]
    return JsonResponse({"subcategories": sub_list})

def add_cart(request):
    return render(request, 'admin/add_cart.html')

def admin_base(request):
    return render(request, 'admin/admin_base.html')

def all_payment(request):
    return render(request, 'admin/all_payment.html')

def contact(request):
    categories = Category.objects.filter(parent__isnull=True)  

    return render(request, 'contact.html',{'categories':categories})


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

def our_products(request):
    total_products = Product.objects.count()

    category_id = request.GET.get('category')  
    query = request.GET.get('q')  
    sort_option = request.GET.get('sort')  

    categories = Category.objects.filter(parent__isnull=True)  
    selected_category = None
    parent_category = None
    subcategories = Category.objects.none()
    products = Product.objects.all()

    # 🔹 Category filter
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)

            if selected_category.parent is None:
                parent_category = selected_category.id
                products = Product.objects.filter(category=selected_category)
            else:
                parent_category = selected_category.parent.id
                products = Product.objects.filter(subcategories=selected_category)

            subcategories = Category.objects.filter(parent_id=parent_category)

        except Category.DoesNotExist:
            selected_category = None
    filtered_count = products.count()  # after category/search filter


    # 🔹 Search filter
    if query:
        products = products.filter(name__icontains=query)

    # 🔹 Sorting
    if sort_option == "price_low":
        products = products.order_by("price")  
    elif sort_option == "price_high":
        products = products.order_by("-price")
    elif sort_option == "latest":
        products = products.order_by("-id")  
    elif sort_option == "rating":
        products = products.order_by("-rating")  
    elif sort_option == "popularity":
        products = products.order_by("-popularity")  

    # 🔹 Pagination
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    page_range = get_page_range(paginator, products_page.number)
    start_index = (products_page.number - 1) * paginator.per_page + 1
    end_index = start_index + len(products_page.object_list) - 1
    total_results = paginator.count

    context = {
        "categories": categories,
        "selected_category": category_id,
        "selected_category_obj": selected_category,
        "parent_category": parent_category,
        "subcategories": subcategories,
        "products": products_page,
        "page_range": page_range,
        "MEDIA_URL": settings.MEDIA_URL,
        "query": query,
        "start_index": start_index,
        "end_index": end_index,
        "total_results": total_results,
        "start_index": products_page.start_index() if filtered_count > 0 else 0,
        "end_index": products_page.end_index() if filtered_count > 0 else 0,
        "filtered_count": filtered_count,    
        "total_products": total_products,      
    }

    return render(request, "our_products.html", context)
