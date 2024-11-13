from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('oci/credentials/', views.oci_credentials_view, name='oci_credentials'),
    path('accounts/register/', views.registrar, name='register'),
    path('oci/instances/', views.listar_instancias_view, name='listar_instancias'),
]