from django.contrib import admin
from .models import Productos, Marca, Categoria, Articulo, Carrito_Compras
# Register your models here.

admin.site.register(Productos)
admin.site.register(Marca)
admin.site.register(Categoria)
admin.site.register(Articulo)
admin.site.register(Carrito_Compras)