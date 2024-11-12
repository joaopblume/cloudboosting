from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def my_vms(request, vm_id):
    return HttpResponse(f"You're looking at Virtual Machine: {vm_id}.")
