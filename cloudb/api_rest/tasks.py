from time import sleep
import logging
from .models import InstanceSchedule, VM
from .models import AWSCredentials, OCICredentials
from .utils import start_vm_oci, stop_vm_oci
from django_q.models import Schedule


logger = logging.getLogger(__name__)

def check_info(schedule_id):
    instance_id = InstanceSchedule.objects.get(id=schedule_id).instance_id

    print('Buscando o usuário')
    user = InstanceSchedule.objects.get(id=schedule_id).user
    print(user)

    print('Buscando o agendamento')
    # Verifica se o agendamento ainda é valido: 
    if not InstanceSchedule.objects.filter(id=schedule_id).exists():
        raise ValueError(f"Agendamento para {schedule_id} não encontrado.")
    print('Agendamento encontrado')
    print('Id do agendamento: ' + str(schedule_id))
        
    print('Buscando a cloud')
    # Busca a cloud
    cloud = VM.objects.get(instance_id=instance_id).cloud.cloud_type

    return user, cloud, instance_id


def start(schedule_id):

    user, cloud, instance_id = check_info(schedule_id)

    if cloud == 'OCI':
        # Busca o config file da OCI
        credentials = OCICredentials.objects.get(user=user)
        print('Credenciais encontradas')
        print(credentials)
        print('Iniciando a VM')
        result = start_vm_oci(credentials, instance_id)
        schedule = InstanceSchedule.objects.get(id=schedule_id)
        while True:
            # Verificar status do Schedule antes de continuar
            schedule.refresh_from_db()  # Atualiza os dados do banco
            if schedule.status == "canceled":
                print("A tarefa foi cancelada. Encerrando execução.")
                return

        
            print('Executando ...')
            sleep(5) 

    elif cloud == 'AWS':
        # Busca o config file da AWS
        credentials = AWSCredentials.objects.get(user=user)
        print('Credenciais encontradas')
        print(credentials)





def start_vm_result(task):
    """
    Função hook para processar o resultado da tarefa start_vm_oci.
    """
    vm_name = task.result['vm_name']
    status = task.result['status']

    print(f'VM {vm_name} iniciada com sucesso.')
    print(f'Status: {status}')



def stop(schedule_id):
    user, cloud, instance_id = check_info(schedule_id)

    if cloud == 'OCI':
        # Busca o config file da OCI

        credentials = OCICredentials.objects.get(user=user)
        print('Credenciais encontradas')
        print(credentials)
        print('Iniciando a VM')
        result = stop_vm_oci(credentials, instance_id)
        return result

    elif cloud == 'AWS':
        # Busca o config file da AWS
        credentials = AWSCredentials.objects.get(user=user)
        print('Credenciais encontradas')
        print(credentials)
    

    print(f"Iniciando a vm {instance_id}")

def stop_vm_result(task):
    vm_name = task.result['vm_name']
    status = task.result['status']

    print(f"VM {vm_name} parada com sucesso.")
    print(f"Status: {status}")

