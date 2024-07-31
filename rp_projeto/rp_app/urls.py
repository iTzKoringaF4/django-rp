from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_qrcode, name='login_qrcode'),
    path('login/', views.login, name='login'),
    path('login_text/', views.login_text, name='login_text'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('marcador/', views.marcador, name='marcador'),
    path('minhas_marcações/', views.minha_marcacao, name='marcações'),
    path('logout/', views.logout, name='logout'),
]