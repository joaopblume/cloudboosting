# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import OCICredentialsForm
from .models import OCICredentials
from .forms import RegistroForm


@login_required
def oci_credentials_view(request):
    try:
        credentials = OCICredentials.objects.get(user=request.user)
    except OCICredentials.DoesNotExist:
        credentials = None

    if request.method == 'POST':
        form = OCICredentialsForm(request.POST, instance=credentials)
        if form.is_valid():
            creds = form.save(commit=False)
            creds.user = request.user
            creds.save()
            return redirect('dashboard')  # Redirecione conforme necessário
    else:
        form = OCICredentialsForm(instance=credentials)

    return render(request, 'oci_credentials_form.html', {'form': form})


def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('oci_credentials')  # Redirecione para onde desejar
    else:
        form = RegistroForm()
    return render(request, 'registration/register.html', {'form': form})