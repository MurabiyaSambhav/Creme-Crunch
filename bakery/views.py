
from django.contrib.auth import logout
from django.shortcuts import redirect,render

def home(request):
    return render(request, "base.html")

def user_logout(request):
    logout(request)
    return redirect('home')
