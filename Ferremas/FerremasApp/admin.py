from django.contrib import admin
from .models import Productos, Marca, Categoria
# Register your models here.

admin.site.register(Productos)
admin.site.register(Marca)
admin.site.register(Categoria)
