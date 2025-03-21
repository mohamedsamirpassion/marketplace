from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Car
from .forms import CarForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

def home(request):
    cars = Car.objects.filter(status='approved')
    return render(request, 'core/home.html', {'cars': cars})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


@login_required
def submit_ad(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            return redirect('home')
    else:
        form = CarForm()
    return render(request, 'core/submit_ad.html', {'form': form})