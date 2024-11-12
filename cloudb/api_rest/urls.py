from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:vm_id>/", views.my_vms, name="my_vms"),

]