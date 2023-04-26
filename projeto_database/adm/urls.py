from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('clientes/', views.cadclient),
    path('produtos/', views.cadprod),
    path('relatoriopedido/', views.relatpedido),
    path('extratopedido/', views.extratopedido),
]

