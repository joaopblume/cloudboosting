# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import OCICredentialsForm
from .models import OCICredentials
from .models import UserCloud
from .utils import listar_instancias_oci, create_oci_config, validar_credenciais
from django.contrib.auth.forms import UserCreationForm




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
                
                UserCloud.objects.get_or_create(user=request.user, cloud_type='OCI')

                
                return redirect('listar_instancias_cloud', cloud_id=request.user.usercloud_set.get(cloud_type='OCI').id)
            else:
                form.add_error(None, "Credenciais inválidas. Por favor, verifique e tente novamente.")
    else:
        form = OCICredentialsForm(instance=credentials)
    return render(request, 'oci_credentials_form.html', {'form': form})



@login_required
def listar_instancias_cloud(request, cloud_id):
    user_cloud = get_object_or_404(UserCloud, id=cloud_id, user=request.user)

    if user_cloud.cloud_type == 'OCI':
        # Obtenha as credenciais OCI do usuário
        credentials = get_object_or_404(OCICredentials, user=request.user)
        
        # Liste as instâncias OCI usando as credenciais
        instances = listar_instancias_oci(credentials)
    else:
        instances = []  # Aqui, você poderia lidar com outras clouds, como AWS e Azure no futuro

    return render(request, 'listar_instancias.html', {
        'cloud': user_cloud,
        'instances': instances
    })

def register(request):
    # Página de registro
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

'''
@login_required
def listar_instancias_view(request):
    try:
        creds = OCICredentials.objects.get(user=request.user)
    except OCICredentials.DoesNotExist:
        # Redirecionar para a página de configuração das credenciais
        return redirect('oci_credentials')

    instances = listar_instancias(creds)
    return render(request, 'listar_instancias.html', {'instances': instances})
'''

@login_required
def user_home(request):
    user_clouds = UserCloud.objects.filter(user=request.user)
    return render(request, 'user_home.html', {'user_clouds': user_clouds})


def index(request):
    # Página inicial
    return render(request, 'index.html')


def register_cloud(request):
    clouds = [
        {'name': 'OCI', 'url': 'oci'},
        {'name': 'AWS', 'url': 'aws'},
        {'name': 'Azure', 'url': 'azure'},
    ]
    return render(request, 'register_cloud.html', {'clouds': clouds})


def cloud_credentials(request, cloud_name):
    if cloud_name == 'oci':
        return redirect('oci_credentials')  # redireciona para a página de credenciais da OCI
    elif cloud_name == 'aws':
        # Redireciona para a página de configuração do AWS, quando disponível
        pass
    elif cloud_name == 'azure':
        # Redireciona para a página de configuração do Azure, quando disponível
        pass
    else:
        # Cloud não suportada
        return redirect('register_cloud')