from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .utils.zerobounce import verify_email_with_zerobounce

CustomUser = get_user_model()


def base(request):
    return render(request, "base.html")

def home(request):
    return render(request, "home.html")


def register(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()

    #  Gmail-only
    if not email.endswith("@gmail.com"):
        return JsonResponse({"success": False, "message": "Please enter a Gmail address"})

    #  ZeroBounce validation
    result = verify_email_with_zerobounce(email)
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
