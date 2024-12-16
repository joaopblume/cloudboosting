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
from .models import Schedule
from .models import WeeklySchedule, MonthlySchedule
from .models import CombinedScheduleView
from .utils import listar_instancias_oci, create_oci_config, validar_credenciais, validar_credenciais_aws, listar_instancias_aws
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django_q.tasks import async_task
from django.http import HttpResponseBadRequest
from .schedule import process_schedule
from django.db import transaction
import json
from collections import defaultdict
from itertools import groupby
from operator import itemgetter




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

    if request.method == "POST":
        try:
            # Recuperar os dados do formulário
            intervals_data = request.POST.get("intervals", "[]")  
            repetition_data = request.POST.get("repetition", "{}")  

            # Decodificar JSON
            intervals_data = json.loads(intervals_data) 
            repetition_data = json.loads(repetition_data)  
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid intervals or repetition data.")

        if not intervals_data:
            return HttpResponseBadRequest("No intervals provided.")

        # Criar o agendamento principal (Schedule)
        schedule = Schedule.objects.create(
            instance_id=instance_id,
            user=request.user,
        )

        # Salvar intervalos de acordo com o tipo de repetição
        repetition_type = repetition_data.get("type")
        saved_intervals = []

        if repetition_type == "weekly":
            days = repetition_data.get("days", [])  # Lista de dias da semana
            if not days:
                return HttpResponseBadRequest("No days provided for weekly repetition.")

            for day in days:
                for interval in intervals_data:
                    inicio = interval.get("inicio")
                    fim = interval.get("fim")

                    # Validar horários
                    if not inicio or not fim or inicio >= fim:
                        return HttpResponseBadRequest("Invalid 'inicio' or 'fim' for interval.")

                    weekly_schedule = WeeklySchedule.objects.create(
                        schedule=schedule,
                        day_of_week=day,
                        time_interval_start=inicio,
                        time_interval_end=fim,
                    )
                    saved_intervals.append(weekly_schedule)

        elif repetition_type == "monthly":
            days_of_month = repetition_data.get("days_of_month", [])  # Lista de dias do mês
            if not days_of_month:
                return HttpResponseBadRequest("No days provided for monthly repetition.")

            for day in days_of_month:
                for interval in intervals_data:
                    inicio = interval.get("inicio")
                    fim = interval.get("fim")

                    # Validar horários
                    if not inicio or not fim or inicio >= fim:
                        return HttpResponseBadRequest("Invalid 'inicio' or 'fim' for interval.")

                    monthly_schedule = MonthlySchedule.objects.create(
                        schedule=schedule,
                        day_of_month=day,
                        time_interval_start=inicio,
                        time_interval_end=fim,
                    )
                    saved_intervals.append(monthly_schedule)

        else:
            return HttpResponseBadRequest("Invalid repetition type.")

        # Processar agendamento assíncrono (se aplicável)
        transaction.on_commit(lambda: process_schedule(intervals_data, repetition_data, schedule.id))

        return redirect("listar_instancias_cloud", cloud_id=vm.cloud.id)

    # Dados para renderizar o formulário
    hours = [f"{i:02d}" for i in range(25)]  # Lista de 00 a 24 horas
    week_days = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]

    return render(request, "agendar_vm.html", {"instance_id": instance_id, "hours": hours, "week_days": week_days})



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
    

def listar_agendamentos(request, instance_id):
    # Buscar os schedules agrupados por schedule_id
    schedules = CombinedScheduleView.objects.filter(instance_id=instance_id)
    vm = VM.objects.get(instance_id=instance_id)

    # Agrupamento dos intervalos por schedule_id
    grouped_schedules = defaultdict(lambda: {"user_name": None, "created_at": None, "weekly": defaultdict(list), "monthly": defaultdict(list)})

    for schedule in schedules:
        schedule_data = grouped_schedules[schedule.schedule_id]
        schedule_data["user_name"] = schedule.user_name
        schedule_data["created_at"] = schedule.schedule_created_at

        if schedule.weekly_day:
            schedule_data["weekly"][schedule.weekly_day].append({
                "start": schedule.weekly_start,
                "end": schedule.weekly_end,
            })
        elif schedule.monthly_day:
            schedule_data["monthly"][schedule.monthly_day].append({
                "start": schedule.monthly_start,
                "end": schedule.monthly_end,
            })

    # Convertendo defaultdicts para dicts para simplificar no template
    for schedule_id, schedule_data in grouped_schedules.items():
        schedule_data["weekly"] = dict(schedule_data["weekly"])
        schedule_data["monthly"] = dict(schedule_data["monthly"])

    return render(
        request,
        'listar_agendamentos.html',
        {
            "schedules": grouped_schedules.items(),  # Passar como lista de pares (id, dados)
            "instance_id": instance_id,
            "instance_name": vm.display_name,
        },
    )

def alterar_agendamento(request, schedule_id):
    # Obter o agendamento pelo ID
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == "POST":
        # Dados enviados pelo formulário
        weekly_intervals = request.POST.getlist("weekly_intervals", [])
        monthly_intervals = request.POST.getlist("monthly_intervals", [])

        # Processar os intervalos semanais
        existing_weekly_intervals = WeeklySchedule.objects.filter(schedule_id=schedule_id)
        existing_weekly_map = {
            (interval.day_of_week, interval.time_interval_start, interval.time_interval_end): interval
            for interval in existing_weekly_intervals
        }
        submitted_weekly_map = {
            (day, start, end): {"day": day, "start": start, "end": end}
            for day, start, end in weekly_intervals
        }

        # Identificar intervalos deletados
        deleted_weekly = [
            interval for key, interval in existing_weekly_map.items() if key not in submitted_weekly_map
        ]
        for interval in deleted_weekly:
            interval.delete()

        # Identificar intervalos adicionados
        added_weekly = [
            data for key, data in submitted_weekly_map.items() if key not in existing_weekly_map
        ]
        for data in added_weekly:
            WeeklySchedule.objects.create(
                schedule=schedule,
                day_of_week=data["day"],
                time_interval_start=data["start"],
                time_interval_end=data["end"],
            )

        # Processar os intervalos mensais
        existing_monthly_intervals = MonthlySchedule.objects.filter(schedule_id=schedule_id)
        existing_monthly_map = {
            (interval.day_of_month, interval.time_interval_start, interval.time_interval_end): interval
            for interval in existing_monthly_intervals
        }
        submitted_monthly_map = {
            (day, start, end): {"day": day, "start": start, "end": end}
            for day, start, end in monthly_intervals
        }

        # Identificar intervalos deletados
        deleted_monthly = [
            interval for key, interval in existing_monthly_map.items() if key not in submitted_monthly_map
        ]
        for interval in deleted_monthly:
            interval.delete()

        # Identificar intervalos adicionados
        added_monthly = [
            data for key, data in submitted_monthly_map.items() if key not in existing_monthly_map
        ]
        for data in added_monthly:
            MonthlySchedule.objects.create(
                schedule=schedule,
                day_of_month=data["day"],
                time_interval_start=data["start"],
                time_interval_end=data["end"],
            )

        return redirect("listar_agendamentos", instance_id=schedule.instance_id)
    # Estruturar os intervalos agrupados
    schedule_data = {
        "weekly": defaultdict(list),  # Intervalos semanais agrupados por dia
        "monthly": defaultdict(list),  # Intervalos mensais agrupados por dia
    }

    # Buscar intervalos semanais associados
    weekly_intervals = WeeklySchedule.objects.filter(schedule_id=schedule_id)
    for interval in weekly_intervals:
        schedule_data["weekly"][interval.day_of_week].append({
            "start": interval.time_interval_start.strftime('%H:%M'),  # Converte para string
            "end": interval.time_interval_end.strftime('%H:%M'),      # Converte para string
        })

    # Buscar intervalos mensais associados
    monthly_intervals = MonthlySchedule.objects.filter(schedule_id=schedule_id)
    for interval in monthly_intervals:
        schedule_data["monthly"][interval.day_of_month].append({
            "start": interval.time_interval_start.strftime('%H:%M'),  # Converte para string
            "end": interval.time_interval_end.strftime('%H:%M'),      # Converte para string
        })

    # Converter defaultdict para dict
    schedule_data["weekly"] = dict(schedule_data["weekly"])
    schedule_data["monthly"] = dict(schedule_data["monthly"])

    return render(
        request,
        'alterar_agendamento.html',
        {
            "schedule": schedule,
            "schedule_data": schedule_data,  # Dados agrupados para o template
        },
    )