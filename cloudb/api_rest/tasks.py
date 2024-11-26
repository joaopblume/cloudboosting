from time import sleep
import logging
from .models import InstanceSchedule
from django_q.models import Schedule
from datetime import datetime



logger = logging.getLogger(__name__)

def start_vm(agendamento: InstanceSchedule):
    """
    Função que inicia a VM baseada no ID.
    """
    print("Agendamento recebido:")
    print(agendamento)
    print(f"Iniciando a VM com ID {agendamento.instance_id}")
    print(f"Horario: {agendamento.specific_time}")
        # Aqui você chamaria sua API para iniciar a VM

    schedule_type_map = {
        "daily": Schedule.DAILY,
        "monthly": Schedule.MONTHLY
    }

    schedule_type = schedule_type_map.get(agendamento.frequency, Schedule.ONCE)

    # Calcular o próximo horário de execução
    if agendamento.specific_time:
        dia = agendamento.day_of_week
        print(dia)
        # dia da semana em ingles tudo minusculo
        today = datetime.now().today().strftime('%A').lower()
        specific_time = datetime.strptime(str(agendamento.specific_time), '%H:%M')
        if dia == today:
            # transforma o specific time em datetime  que esta no formato 
            # 00:00 juntando com a data de hoje
            next_run = datetime.now().replace(hour=specific_time.hour, minute=specific_time.minute)
        else:
            # tomorrow at specific time
            next_run = datetime.now().replace(hour=specific_time.hour, minute=specific_time.minute)

    else:
        next_run = datetime.now()

    print(next_run)
    Schedule.objects.create(
        func="api_rest.tasks.executed_task",  # Função a ser chamada
        args=f"[{agendamento.id}]",  # Passar o ID do agendamento como argumento
        schedule_type=schedule_type,  # Tipo de agendamento
        minutes=agendamento.interval if agendamento.interval_unit == "minutes" else None,
        next_run=next_run,  # Próxima execução
        repeats=-1 if agendamento.frequency == "daily" else 1,  # Repetir indefinidamente para diário
        name=f"Agendamento para VM {agendamento.instance_id}"
    )
    print(f"Agendamento criado para {agendamento.instance_id} no Django Q.")

def executed_task(tarefa):
    print("Executando tarefa")
    

def on_task_complete(task):
    print('Agendando tarefa, aguarde...')
    sleep(1)
    print(f"Tarefa agendada com sucesso! Tarefa: {task}")