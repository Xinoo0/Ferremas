from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from .models import Productos
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
    return render(request, 'registro/login.html')

def register(request):
    return render(request, 'registro/register.html')    

# API TRANSBANK
def iniciar_pago(request):
    if request.method == "POST":
        # Obtener el carrito del usuario actual
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

        # Obtener los productos en el carrito
        productos = carrito.articulos.all()
        
        # Calcular el total
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
    
    
def confirmar_pago(request):
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
                producto = articulo.objects.get(id_articulo=producto_id)
                print(f"Producto: {producto.nombre}, Cantidad: {cantidad}")
            
         

            return render(request, 'confirmacion_pago.html', {'response': response})
        else:
            return HttpResponse("No se recibió respuesta de Transbank.")
    except Exception as e:
        return HttpResponse(f"Error interno: {str(e)}")
