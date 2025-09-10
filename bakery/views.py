
from django.contrib.auth import logout
from django.shortcuts import redirect,render

def home(request):
    return render(request, "home.html")

def user_logout(request):
    logout(request)
    return redirect('base')

def base(request):
    return render(request,"base.html")