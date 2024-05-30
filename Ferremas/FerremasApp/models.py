from django.db import models
import uuid
from django.contrib.auth.models import User

# MODELOS DE LA TIENDA

class Categoria(models.Model):
    id_c = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=40)

    def __str__(self):
        return self.nombre_categoria

class Marca(models.Model):
    id_m = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=250)

    def __str__(self):
        return self.nombre_marca

class Productos(models.Model):
    id_p = models.UUIDField(default=uuid.uuid4, primary_key=True)
    nombre_producto = models.CharField(max_length=60, null=False)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, default=0, null=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, default=0, null=False)
    valor = models.IntegerField(null=False)
    foto = models.ImageField(upload_to="img", null=False)
    cantidad = models.IntegerField(default=0, null=False)
    descripcion_producto = models.TextField(null=False, default="Descripcion")

    def __str__(self):
        return self.nombre_producto


# MODELO DE CARRITO
class Carrito_Compras(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    articulo = models.ManyToManyField('articulo', related_name='carrito', blank=True)

    def __str__(self):
        return f"carrito de {self.usuario.username}"

class Articulo(models.Model):
    id_art = models.AutoField(primary_key=True)
    nombre_articulo = models.CharField(max_length=100, blank=False, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre_articulo