# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import OCICredentialsForm
from .forms import AWSCredentialsForm
from .models import OCICredentials
from .models import AWSCredentials
from .models import UserCloud
from .models import VM
from .utils import listar_instancias_oci, create_oci_config, validar_credenciais, validar_credenciais_aws, listar_instancias_aws
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django_q.tasks import async_task
from django.http import HttpResponseBadRequest
from .models import InstanceSchedule
from .tasks import start_vm, on_task_complete



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

                
                #return redirect('listar_instancias_cloud', cloud_id=request.user.usercloud_set.get(cloud_type='OCI').id)
                return redirect('user_home')
            else:
                form.add_error(None, "Credenciais inválidas. Por favor, verifique e tente novamente.")
    else:
        form = OCICredentialsForm(instance=credentials)
    return render(request, 'oci_credentials_form.html', {'form': form})

@login_required
def aws_credentials_view(request):
    if request.method == 'POST':
        form = AWSCredentialsForm(request.POST)
        if form.is_valid():
            creds = form.save(commit=False)
            creds.user = request.user
            access_key = creds.access_key
            secret_key = creds.secret_key
            # Valida as credenciais
            if validar_credenciais_aws(access_key, secret_key):
                # Se as credenciais forem válidas, salva a cloud no UserCloud
                creds.save()
                UserCloud.objects.get_or_create(user=request.user, cloud_type='AWS')
                #return redirect('listar_instancias_cloud', cloud_id=request.user.usercloud_set.get(cloud_type='AWS').id)     
                return redirect('user_home')
            else:
                form.add_error(None, "Credenciais inválidas. Por favor, verifique e tente novamente.")
    else:
        form = AWSCredentialsForm()

    return render(request, 'aws_credentials_form.html', {'form': form})

@login_required
def listar_instancias_cloud(request, cloud_id):
    user_cloud = get_object_or_404(UserCloud, id=cloud_id, user=request.user)
    
    # Verificar o tipo de nuvem
    if user_cloud.cloud_type == 'OCI':
        credentials = get_object_or_404(OCICredentials, user=request.user)
        api_instances = listar_instancias_oci(credentials)
    elif user_cloud.cloud_type == 'AWS':
        aws_credentials = get_object_or_404(AWSCredentials, user=request.user)
        api_instances = listar_instancias_aws(aws_credentials)
    else:
        api_instances = []

    # Buscar instâncias já salvas no banco
    cached_instances = VM.objects.filter(user=request.user, cloud=user_cloud)
    cached_ids = {vm.instance_id for vm in cached_instances}

    # Atualizar cache com novas instâncias
    for instance in api_instances:
        if instance['id'] not in cached_ids:
            VM.objects.create(
                user=request.user,
                cloud=user_cloud,
                instance_id=instance['id'],
                display_name=instance['display_name'],
                cpu_count=instance.get('cpu_count', 0),
                memory_gb=instance.get('memory_gb', 0.0),
                lifecycle_state=instance['lifecycle_state'],
                compartment_name=instance.get('compartment_name', ''),
            )
        else:
            # Atualizar as instâncias já existentes
            vm = cached_instances.get(instance_id=instance['id'])
            vm.display_name = instance['display_name']
            vm.cpu_count = instance.get('cpu_count', vm.cpu_count)
            vm.memory_gb = instance.get('memory_gb', vm.memory_gb)
            vm.lifecycle_state = instance['lifecycle_state']
            vm.compartment_name = instance.get('compartment_name', vm.compartment_name)
            vm.save()

    # Retornar instâncias atualizadas do banco
    all_instances = VM.objects.filter(user=request.user, cloud=user_cloud)

    return render(request, 'listar_instancias.html', {
        'cloud': user_cloud,
        'instances': all_instances
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

def login_view(request):
    # Página de login
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('user_home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_home(request):
    user_clouds = UserCloud.objects.filter(user=request.user)
    return render(request, 'user_home.html', {'user_clouds': user_clouds})

@login_required
def agendar_vm(request, instance_id):
    vm = get_object_or_404(VM, instance_id=instance_id, user=request.user)
    user_cloud = vm.cloud

    if request.method == "POST":
        # Validação condicional para campos opcionais
        
        # Prepare os dados para salvar no banco
        schedule_data = {
            "instance_id": instance_id,
            "user": request.user,
            "frequency": request.POST.get("frequency"),
            "week_days": request.POST.get("week_days", ""),
            "specific_time": request.POST.get("specific_time") or None,
            "time_option": request.POST.get("time_option"),
            "interval": int(request.POST.get("interval")) if request.POST.get("interval") else None,
            "interval_unit": request.POST.get("interval_unit"),
            "time_from": request.POST.get("time_from") or None,
            "time_to": request.POST.get("time_to") or None,
            "occurrence": request.POST.get("occurrence"),
            "day_of_week": request.POST.get("day_of_week"),
            "calendar_day": int(request.POST.get("calendar_day")) if request.POST.get("calendar_day") else None,
        }

        # Rules for required fields
        if schedule_data["frequency"] == "monthly" and schedule_data["occurrence"] == "day_of_month" and not schedule_data["calendar_day"]:
            return HttpResponseBadRequest("Calendar day is required for 'Day of Month'.")
        
        if schedule_data["frequency"] == "daily" and not schedule_data["specific_time"] and schedule_data["time_option"] != "several":
            return HttpResponseBadRequest("Specific time is required for 'Daily' frequency.")
        
        if schedule_data["frequency"] == "daily" and not schedule_data["week_days"]:
            return HttpResponseBadRequest("Week days are required for 'Daily' frequency.")

        if schedule_data["time_option"] == "several" and (not schedule_data["time_from"] or not schedule_data["time_to"]):
            return HttpResponseBadRequest("Time from and time to are required for 'Several Times a Day' time option.")
        
        # And so on...

        # Objective: Apply my learnings from logic classes from university, reducing if statements using propositional logic 
        # and boolean algebra. This is a good opportunity to apply my knowledge in practice.

        # Save the schedule in the database
        try:
            schedule = InstanceSchedule.objects.create(**schedule_data)
            schedule.save()

            async_task(
                "api_rest.tasks.start_vm", # Nome da função a ser executada
                schedule, # Argumentos da função
                hook="api_rest.tasks.on_task_complete" # Função de callback
            )
            pass
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        
        return redirect("listar_instancias_cloud", cloud_id=user_cloud.id)

    week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    return render(request, "agendar_vm.html", {"week_days": week_days, "instance_id": instance_id})



def index(request):
    return render(request, 'index.html')

@login_required
def register_cloud(request):
    clouds = [
        {'name': 'OCI', 'url': 'oci', 'logo': 'images/oci_logo.png' },
        {'name': 'AWS', 'url': 'aws', 'logo': 'images/aws_logo.png'},
        {'name': 'Azure', 'url': 'azure', 'logo': 'images/azure_logo.jpg'},
    ]
    return render(request, 'register_cloud.html', {'clouds': clouds})


@login_required
def cloud_credentials(request, cloud_name):
    if cloud_name == 'oci':
        return redirect('oci_credentials')  # redireciona para a página de credenciais da OCI
    elif cloud_name == 'aws':
        return redirect('aws_credentials')        
    elif cloud_name == 'azure':
        # Redireciona para a página de configuração do Azure, quando disponível
        pass
    else:
        # Cloud não suportada
        return redirect('register_cloud')