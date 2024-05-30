from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns=[
    path('', views.index, name="index"),
    path('nosotros', views.nosotros, name="nosotros"),

    # URLS TIENDA
    path('tienda', views.tienda, name="tienda"),

    # URLS USUARIOS

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('accounts/profile/', views.profiles, name='profile'),
]
