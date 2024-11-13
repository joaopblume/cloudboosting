from django.urls import path
from . import views

urlpatterns = [
    path('oci/credentials/', views.oci_credentials_view, name='oci_credentials'),
    path('accounts/register/', views.registrar, name='register'),
]