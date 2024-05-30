from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Productos
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
import json
from rest_framework import viewsets, permissions
# FROMS TRANSBANK
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from .serializers import ProductoSerializer

# Create your views here.

def index(request):
    context={}
    return render(request, 'web/index.html', context)

def nosotros(request):
    return render(request, 'web/nosotros.html')


# VISTAS TIENDA

class ProductoViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Productos.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

def tienda(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            peticion = json.loads(request.body)
            categoria = peticion.get('categoria')
            
            if categoria == "todos":
                productos = Productos.objects.all()
            else:
                productos = Productos.objects.filter(categoria_id=categoria)

            data = {
                "productos" : productos,
            }
            return render(request, 'compras/tienda.html', data)
        else:
            productos = Productos.objects.all()
            data = {
                "productos" : productos,
            }
            return render(request, 'compras/tienda.html', data)
    else:
        if request.method == 'POST':
            peticion = json.loads(request.body)
            categoria = peticion.get('categoria')
            
            if categoria == "todos":
                productos = Productos.objects.all()
            else:
                productos = Productos.objects.filter(categoria_id=categoria)

            data = {
                "productos" : productos,
            }
            return render(request, 'compras/tienda.html', data)
        else:
            productos = Productos.objects.all()
            data = {
                "productos" : productos,
            }
            return render(request, 'compras/tienda.html', data) 


# VISTAS USUARIOS
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})
    elif request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index.html')
        return render(request, 'login.html', {'form': form, 'error': 'Nombre de usuario o contraseña incorrectos'})

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                auth_login(request, user)  # Autenticar al usuario después de registrarse
                messages.success(request, '¡Te has registrado correctamente!')
                return redirect('index.html')
            except IntegrityError:
                return render(request, 'register', {
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'
                })
        return render(request, 'register.html', {
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden'
        })

def logout(request):
    logout(request)
    return redirect('index.html')

def profiles(request):
    user = request.user
    context = {'user': user}
    return render(request, 'profile.html', context)
  

# API TRANSBANK
