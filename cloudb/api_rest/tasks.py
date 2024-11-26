from time import sleep
import logging
from .models import InstanceSchedule, VM


logger = logging.getLogger(__name__)

def start_vm(schedule: InstanceSchedule):
    """
    Função que inicia a VM baseada no ID.
    """
    print(f"Iniciando a VM com ID {schedule.instance_id}")
    print(f"Horario: {schedule.specific_time}")
        # Aqui você chamaria sua API para iniciar a VM

        
def on_task_complete(task):
    print('Esperando 30 seg')
    sleep(30)
    print(f"Tarefa concluída com sucesso! Tarefa: {task}")