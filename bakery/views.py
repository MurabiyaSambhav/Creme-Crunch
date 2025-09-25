from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from django.conf import settings
from .models import BakeryCategory, Product, Weight, ContactForm, ProductImages
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
import re, json

CustomUser = get_user_model()

# ----------------------------
# Base 
# ----------------------------
def base(request):
    return render(request, "base.html")

# ----------------------------
# Home
# ----------------------------

def home(request):
    main_categories = BakeryCategory.objects.filter(parent__isnull=True)

    category_data = []
    for cat in main_categories:
        last_product = Product.objects.filter(category=cat).order_by('-id').first()
        main_image = None
        if last_product:
            main_image_obj = last_product.images.filter(is_main=True).first()
            if main_image_obj:
                main_image = main_image_obj.image.url

        category_data.append({
            'category': cat,
            'last_product': last_product,
            'main_image': main_image
        })

    categories = BakeryCategory.objects.all()  

    return render(request, "home.html", {
        "category_data": category_data,  
        "categories": categories          
    })


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
    # Only top-level categories, prefetch their children
    categories = BakeryCategory.objects.filter(parent__isnull=True).prefetch_related('children')

    # Prepare JSON for JS: include subcategories for each top-level category
    categories_json = [
        {
            'id': cat.id,
            'name': cat.name,
            'subcategories': [{'id': child.id, 'name': child.name} for child in cat.children.all()]
        }
        for cat in categories
    ]

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_ids = request.POST.getlist("subcategories")  # Hidden inputs from JS
        weights = request.POST.getlist("weights[]")
        prices = request.POST.getlist("prices[]")
        images = request.FILES.getlist("images[]")
        main_index = int(request.POST.get("main_image", 0))

        # Create product with selected top-level category
        product = Product.objects.create(
            name=name,
            description=description,
            category_id=category_id if category_id else None,
        )

        # Add subcategories (ManyToMany)
        if subcategory_ids:
            subcategories = BakeryCategory.objects.filter(id__in=subcategory_ids)
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

    return render(request, "admin/add_product.html", {
        "categories": categories,
        "categories_json": json.dumps(categories_json, cls=DjangoJSONEncoder)
    })

# ----------------------------
# All Products
# ----------------------------

def our_products(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    sort_option = request.GET.get("sort")

    products = Product.objects.all()
    selected_category = None
    parent_category = None

    # --------- Filter by category/subcategory ---------
    if category_id:
        try:
            selected_category = BakeryCategory.objects.get(id=category_id)

            if selected_category.parent:
                # Subcategory selected: filter products assigned to this subcategory OR directly assigned category
                products = products.filter(
                    Q(subcategories__id=selected_category.id) | Q(category=selected_category)
                ).distinct()
                parent_category = selected_category.parent.id
            else:
                # Main category selected: include all products in category + all its subcategories
                sub_ids = selected_category.children.values_list('id', flat=True)
                products = products.filter(
                    Q(category=selected_category) | Q(subcategories__id__in=sub_ids)
                ).distinct()
                parent_category = selected_category.id

        except BakeryCategory.DoesNotExist:
            selected_category = None

    # --------- Search ---------
    if query:
        products = products.filter(name__icontains=query)

    # --------- Sorting ---------
    if sort_option == "price_low":
        products = products.order_by("weights__price")
    elif sort_option == "price_high":
        products = products.order_by("-weights__price")
    elif sort_option == "latest":
        products = products.order_by("-id")

    # --------- Pagination ---------
    paginator = Paginator(products.distinct(), 9)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    # Attach main image & first weight
    for p in products_page:
        p.main_image = p.images.filter(is_main=True).first()
        p.first_weight = p.weights.first()

    # Categories for sidebar/filter
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    subcategories = BakeryCategory.objects.filter(parent__isnull=False)

    context = {
        "products": products_page,
        "categories": categories,
        "subcategories": subcategories,
        "selected_category": selected_category,
        "parent_category": parent_category,
        "query": query,
        "page_range": get_page_range(paginator, products_page.number),
        "total_results": products.count(),
        "start_index": products_page.start_index(),
        "end_index": products_page.end_index(),
    }

    return render(request, "our_products.html", context)

# ----------------------------
# Categories
# ----------------------------
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")
        parent_id = request.POST.get("parent")
        subcategories = request.POST.getlist("subcategories[]")  # <-- get all subcategory inputs

        parent = None
        if parent_id:
            try:
                parent = BakeryCategory.objects.get(id=parent_id)
            except BakeryCategory.DoesNotExist:
                parent = None

        # Create or get main category
        category, created = BakeryCategory.objects.get_or_create(name=category_name, parent=parent)

        # Create subcategories (if any)
        for sub_name in subcategories:
            if sub_name.strip():  # ignore empty inputs
                BakeryCategory.objects.get_or_create(name=sub_name.strip(), parent=category)

        return redirect("add_category")

    # For GET, send all categories (so you can select parent for merged table)
    categories = BakeryCategory.objects.all()
    return render(request, "admin/add_category.html", {"categories": categories})

# ----------------------------
# Contact & About
# ----------------------------
def contact(request):
    categories = BakeryCategory.objects.filter(parent__isnull=True)
    return render(request, 'contact.html', {'categories': categories})

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
        categories = BakeryCategory.objects.all()
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
    total_pages = paginator.num_pages
    if total_pages <= max_pages:
        return range(1, total_pages + 1)

    page_range = []
    page_range.append(1)

    if current_page > 3:
        page_range.append("...")

    start = max(2, current_page - 1)
    end = min(total_pages - 1, current_page + 1)
    page_range.extend(range(start, end + 1))

    if current_page < total_pages - 2:
        page_range.append("...")

    page_range.append(total_pages)

    return page_range

# ----------------------------
# Product Suggestions (AJAX) 
# ----------------------------
def product_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        ).distinct()[:10]

        for product in products:
            suggestions.append({
                'id': product.id,
                'name': product.name,
                'category': product.category.name if product.category else ''
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
    categories = BakeryCategory.objects.all()

    return render(request, 'admin/master_list.html', {'products': products, 'categories': categories})
