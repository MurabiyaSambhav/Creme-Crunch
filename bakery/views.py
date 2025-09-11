from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()

from .models import CustomUser

def base(request):
    return render(request, "base.html")

def home(request):
    return render(request, "home.html")

@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # Validate email
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({"success": False, "message": "Enter a valid email"})

        # Check duplicate
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already exists"})

        try:
            # Use create_user for custom user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                address=address
            )
            return JsonResponse({"success": True, "message": "Registration successful"})
        except Exception as e:
            # Return the error as JSON for debugging
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
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
