from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def shop(request):
    return render(request, 'shop.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember:
                request.session.set_expiry(0)  # Session expires when browser closes
            
            # Role-based redirection
            if user.role == 'SYSTEM_ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'STOCK_MANAGER':
                return redirect('stock_dashboard')
            elif user.role == 'SALES_MANAGER':
                return redirect('sales_dashboard')
            elif user.role == 'COMPANY_MANAGER':
                return redirect('company_dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')