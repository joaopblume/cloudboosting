from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_cloud/', views.register_cloud, name='register_cloud'),
    path('register_cloud/<str:cloud_name>/', views.cloud_credentials, name='cloud_credentials'),
    path('oci/credentials/', views.oci_credentials_view, name='oci_credentials'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('cloud/<int:cloud_id>/instancias/', views.listar_instancias_cloud, name='listar_instancias_cloud'),
    path('aws/credentials/', views.aws_credentials_view, name='aws_credentials'),
    path('home/', views.user_home, name='user_home'),
]