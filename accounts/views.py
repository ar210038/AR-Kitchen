# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Order 
from .forms import CustomRegisterForm

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Welcome.")
            return redirect('shop:checkout')
    else:
        form = CustomRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_page = request.POST.get('next') or request.GET.get('next')
            return redirect(next_page or 'shop:shop')
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
        'next': request.GET.get('next', '')
    }
    return render(request, 'accounts/login.html', context)    

def profile(request):
    orders = Order.objects.filter(phone=request.user.username).order_by('-created')[:10]  # Last 10 orders
    return render(request, 'accounts/profile.html', {'orders': orders})

@login_required
def profile(request):
    orders = request.user.orders.all().order_by('-created')[:10]
    return render(request, 'accounts/profile.html', {'orders': orders})