from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import random
import re
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

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({"success": False, "message": "Enter a valid email"})

        # Allow only Gmail accounts
        if not email.lower().endswith("@gmail.com"):
            return JsonResponse({"success": False, "message": "Please enter a Gmail address"})

        # Check for duplicate email
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already exists"})

        try:
            # Generate OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['registration_data'] = {
                "username": username,
                "email": email,
                "password": password,
                "phone": phone,
                "address": address
            }

            # Send OTP to Gmail
            send_mail(
                "Your OTP for Registration",
                f"Your OTP is {otp}",
                "yourgmail@gmail.com",  # Replace with your sender email
                [email],
                fail_silently=False,
            )

            # Inform frontend that OTP is sent
            return JsonResponse({
                "success": True,
                "message": "OTP sent to your Gmail. Please verify to complete registration."
            })

        except Exception as e:
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


def verify_otp_view(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        data = request.session.get("registration_data")

        if not session_otp or not data:
            return JsonResponse({
                "success": False,
                "message": "Session expired. Please register again."
            })

        if str(entered_otp) != str(session_otp):
            return JsonResponse({
                "success": False,
                "message": "Invalid OTP. Try again."
            })

        # Create user (works for all users: normal/admin handled by your user model)
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            address=data['address']
        )

        # Clear session
        request.session.pop('otp')
        request.session.pop('registration_data')

        return JsonResponse({
            "success": True,
            "message": "Registration successful! Please login."
        })

    return JsonResponse({
        "success": False,
        "message": "Invalid request."
    })
