# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import OCICredentialsForm
from .models import OCICredentials
from .forms import RegistroForm
from .utils import listar_instancias, create_oci_config, validar_credenciais



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
            config = create_oci_config(creds)
            if validar_credenciais(config):
                creds.save()
                return redirect('listar_instancias')
            else:
                form.add_error(None, "Credenciais inválidas. Por favor, verifique e tente novamente.")
    else:
        form = OCICredentialsForm(instance=credentials)
    return render(request, 'oci_credentials_form.html', {'form': form})


def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')  # Redirecione para onde desejar
    else:
        form = RegistroForm()
    return render(request, 'registration/register.html', {'form': form})


def index(request):
    # Retorna um simples ola mundo
    return render(request, 'index.html')


@login_required
def listar_instancias_view(request):
    try:
        creds = OCICredentials.objects.get(user=request.user)
    except OCICredentials.DoesNotExist:
        # Redirecionar para a página de configuração das credenciais
        return redirect('oci_credentials')

    instances = listar_instancias(creds)
    return render(request, 'listar_instancias.html', {'instances': instances})