from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.db import IntegrityError
from .models import BakeryCategory, Product, Weight, ContactForm, ProductImages, BakeryCart
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from django.urls import reverse
from django.db.models import Q
import re, json, traceback
from django.conf import settings

CustomUser = get_user_model()

# ----------------------------
# Admin Pages
# ----------------------------
def admin_base(request):
    return render(request, 'admin/admin_base.html')

# ----------------------------
# Base
# ----------------------------
def base(request):
    return render(request, "base.html")

# ----------------------------
# Home
# ----------------------------
def home(request):
    # Get all main categories (parent is null)
    main_categories = BakeryCategory.objects.filter(parent__isnull=True)
    category_data = []

    for cat in main_categories:
        main_image = None

        # Use image filename directly from the DB if available
        if getattr(cat, "image", None) and cat.image.strip():
            main_image = f"{settings.MEDIA_URL}products/{cat.image}"

        category_data.append({
            'category': cat,
            'main_image': main_image
        })

    # Optional: get all categories for filtering or menus
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
    categories = BakeryCategory.objects.filter(parent__isnull=True).prefetch_related('children')
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
        subcategory_ids = request.POST.getlist("subcategories")
        weights = request.POST.getlist("weights[]")
        prices = request.POST.getlist("prices[]")
        images = request.FILES.getlist("images[]")
        main_index = int(request.POST.get("main_image", 0))

        product = Product.objects.create(
            name=name,
            description=description,
            category_id=category_id if category_id else None,
        )

        if subcategory_ids:
            subcategories = BakeryCategory.objects.filter(id__in=subcategory_ids)
            product.subcategories.set(subcategories)

        for w, p in zip(weights, prices):
            if w.strip() and str(p).strip():
                Weight.objects.create(
                    product=product,
                    weight=w.strip(),
                    price=float(p.strip())
                )

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

    # Filter by category/subcategory
    if category_id:
        try:
            selected_category = BakeryCategory.objects.get(id=category_id)
            if selected_category.parent:
                products = products.filter(
                    Q(subcategories__id=selected_category.id) | Q(category=selected_category)
                ).distinct()
                parent_category = selected_category.parent.id
            else:
                sub_ids = selected_category.children.values_list('id', flat=True)
                products = products.filter(
                    Q(category=selected_category) | Q(subcategories__id__in=sub_ids)
                ).distinct()
                parent_category = selected_category.id
        except BakeryCategory.DoesNotExist:
            selected_category = None

    if query:
        products = products.filter(name__icontains=query)

    if sort_option == "price_low":
        products = products.order_by("weights__price")
    elif sort_option == "price_high":
        products = products.order_by("-weights__price")
    elif sort_option == "latest":
        products = products.order_by("-id")

    paginator = Paginator(products.distinct(), 9)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    for p in products_page:
        p.main_image = p.images.filter(is_main=True).first()
        p.first_weight = p.weights.first()

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
        subcategories = request.POST.getlist("subcategories[]")
        parent = None
        if parent_id:
            parent = BakeryCategory.objects.filter(id=parent_id).first()

        category, _ = BakeryCategory.objects.get_or_create(name=category_name, parent=parent)

        for sub_name in subcategories:
            if sub_name.strip():
                BakeryCategory.objects.get_or_create(name=sub_name.strip(), parent=category)

        return redirect("add_category")

    categories = BakeryCategory.objects.all()
    return render(request, "admin/add_category.html", {"categories": categories})

# ----------------------------
# Add to Cart
# ----------------------------

@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get("cart", {})
        pid_str = str(product_id)
        if pid_str not in cart:
            cart[pid_str] = {
                "name": product.name,
                "quantity": 1,
                "price": float(product.price),
            }
        else:
            cart[pid_str]["quantity"] += 1
        request.session["cart"] = cart
        request.session.modified = True
        return JsonResponse({"success": True, "cart": cart})
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

def add_cart(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            product_id = data.get('product_id')
            weight_id = data.get('weight_id')
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                quantity = 1

            if not product_id or not weight_id:
                return JsonResponse({'status': 'error', 'message': 'Product or weight not provided.'}, status=400)

            product = get_object_or_404(Product.objects.prefetch_related('weights', 'images', 'category'), id=product_id)

            # Access weight safely
            try:
                weight = product.weights.get(id=weight_id)
            except AttributeError:
                weight = product.weight_set.get(id=weight_id)

            category = getattr(product, 'category', None)

            try:
                price = Decimal(weight.price)
            except (TypeError, InvalidOperation):
                price = Decimal('0.00')

            cart_item, created = BakeryCart.objects.get_or_create(
                user=request.user,
                product=product,
                weight=weight,
                defaults={'quantity': quantity, 'price': price, 'category': category}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Return updated cart items for frontend refresh
            cart_qs = BakeryCart.objects.filter(user=request.user)
            items = [{
                'name': c.product.name,
                'quantity': c.quantity,
                'total_price': float(c.quantity * c.price)
            } for c in cart_qs]

            return JsonResponse({
                'status': 'success',
                'message': f"{product.name} ({quantity}) added to cart.",
                'cart_items': items
            })

        # Optional: reject GET for AJAX add_cart
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
 
# ----------------------------
# Checkout                    
# ----------------------------

def checkout_view(request):
    # your checkout logic
    return render(request, 'checkout.html')

# ----------------------------
# Cart Items (for header display)
# ----------------------------

@login_required
def cart_items(request):
    cart = request.session.get('cart', {})
    print("DEBUG CART:", cart)  # check what’s inside

    items = []
    for product_id, data in cart.items():
        items.append({
            'name': data.get('name', 'Unknown'),
            'quantity': data.get('quantity', 0),
            'total_price': data.get('quantity', 0) * data.get('price', 0),
        })
    return JsonResponse({'items': items})

@login_required
def add_to_cart(request, product_id):

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get("cart", {})

        pid_str = str(product_id)
        if pid_str not in cart:
            cart[pid_str] = {
                "name": product.name,
                "quantity": 1,
                "price": float(product.price),
            }
        else:
            cart[pid_str]["quantity"] += 1

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({"success": True, "cart": cart})

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

# ----------------------------
# Contact & About
# ----------------------------

def contact(request):
    categories = BakeryCategory.objects.all()
    return render(request, "contact.html", {"categories": categories})

def about_us(request):
    categories = BakeryCategory.objects.all()
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
    return render(request, 'about_us.html', {'categories': categories, 'success': False})

def contact_detail(request):
    contacts = ContactForm.objects.values("id", "name", "email", "phone", "message", "submitted_at", "created_at", "updated_at").order_by("-submitted_at")
    return render(request, 'admin/contact_details.html', {"contacts": contacts})

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

    page_range = [1]
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
# Product Suggestions
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

def all_payment(request):
    return render(request, 'admin/all_payment.html')

def list(request):
    products = Product.objects.all().prefetch_related('weights', 'images')
    categories = BakeryCategory.objects.all()
    return render(request, 'admin/master_list.html', {'products': products, 'categories': categories})
