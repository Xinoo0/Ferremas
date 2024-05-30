from django.urls import path
from . import views


urlpatterns=[
    path('', views.index, name="index"),
    path('nosotros', views.nosotros, name="nosotros"),

    # URLS TIENDA
    path('tienda', views.tienda, name="tienda"),

    # URLS USUARIOS
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
]