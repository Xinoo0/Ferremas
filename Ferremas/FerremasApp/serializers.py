from .models import Productos
from rest_framework import serializers

class ProductoSerializer(serializers.ModelSerializer):
    marca = serializers.CharField(source='marca.nombre', read_only=True)

    class Meta:
        model = Productos
        exclude = ['imagen', 'categoria']