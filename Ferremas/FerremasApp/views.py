from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Productos, Articulo, Carrito_Compras
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
import json
from rest_framework import viewsets, permissions
# FROMS TRANSBANK
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from .serializers import ProductoSerializer
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.urls import reverse
import hashlib
from transbank.common.integration_type import IntegrationType


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
        return render(request, 'registration/login.html', {'form': AuthenticationForm()})
    elif request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index.html')
        return render(request, 'registration/login.html', {'form': form, 'error': 'Nombre de usuario o contraseña incorrectos'})

def register(request):
    if request.method == 'GET':
        return render(request, 'registration/register.html', {'form': UserCreationForm()})
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
                return render(request, 'register.html', {
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'
                })
        return render(request, 'registration/register.html', {
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden'
        })

def logout(request):
    logout(request)
    return redirect('web/index.html')

def profiles(request):
    user = request.user
    context = {'user': user}
    return render(request, 'profile.html', context)
  
# VISTAS CARRITOS

def carrito(request):
    articulos = Articulo.objects.all()
    total = sum(float(articulo.valor) for articulo in articulos)  
    print("Artículos:", articulos)
    print("Total:", total)
    return render(request, 'compras/Carrito.html', {'articulos': articulos, 'total': total})



def eliminar(request):
    if request.method == "POST":
        Articulo.objects.all().delete()
        return redirect(request.META.get('HTTP_REFERER', 'Productos'))
    return redirect('Productos')


def agregar(request):
    if request.method == "POST":
        nombre_articulo = request.POST.get('nombre')
        valor = request.POST.get('precio')
        carrito, creado = Carrito_Compras.objects.get_or_create(usuario=request.user)
        nuevo_articulo = Articulo(nombre_articulo=nombre_articulo, valor=valor)
        nuevo_articulo.save()
        carrito.articulo.add(nuevo_articulo)
        return redirect(request.META.get('HTTP_REFERER', 'compras/carrito.html'))
    return redirect('compras/carrito.htm')


# API TRANSBANK

def pagar(request):
    if request.method == "POST":
        carrito, creado = Carrito_Compras.objects.get_or_create(usuario=request.user)
        productos = carrito.articulo.all()
        total = sum(producto.precio for producto in productos)
        
        if total > 0:
            session_key = request.session.session_key
            buy_order = hashlib.md5(session_key.encode()).hexdigest()[:26]
            session_id = f"sesion_{session_key}"
            amount = total
            return_url = request.build_absolute_uri(reverse('confirmar_pago'))

            tx = Transaction(WebpayOptions(settings.TRANBANK_COMMERCE_CODE, settings.TRANBANK_API_KEY, IntegrationType.TEST))
            try:
                response = tx.create(buy_order, session_id, amount, return_url)
                if response:
                    return redirect(response['url'] + "?token_ws=" + response['token'])
                else:
                    return HttpResponse("No se recibió respuesta de Transbank.")
            except Exception as e:
                return HttpResponse(f"Error interno: {str(e)}")
        else:
            return HttpResponse("El carrito está vacío.")
    else:
        return HttpResponse("Método no permitido.", status=405)
    
    
def comprobante_pago(request):
    token_ws = request.GET.get('token_ws')
    if not token_ws:
        return HttpResponse("Token no proporcionado.")

    try:
        tx = Transaction(WebpayOptions(settings.TRANBANK_COMMERCE_CODE, settings.TRANBANK_API_KEY, IntegrationType.TEST))
        response = tx.commit(token_ws)
        if response and response['status'] == 'AUTHORIZED':

            # Obtener el carrito de la sesión
            carrito = request.session.get('carrito', {})
            
            for producto_id, cantidad in carrito.items():
                producto = Articulo .objects.get(id_articulo=producto_id)
                print(f"Producto: {producto.nombre_articulo}, Cantidad: {cantidad}")
            
         

            return render(request, 'confirmacion_pago.html', {'response': response})
        else:
            return HttpResponse("No se recibió respuesta de Transbank.")
    except Exception as e:
        return HttpResponse(f"Error interno: {str(e)}")