from time import sleep
import logging
from .models import Schedule, VM
from .models import AWSCredentials, OCICredentials
from .utils import start_vm_oci, stop_vm_oci, start_vm_aws, stop_vm_aws

logger = logging.getLogger(__name__)

def check_info(schedule_id):
    instance_id = Schedule.objects.get(id=schedule_id).instance_id

    print('Buscando o usuário')
    user = Schedule.objects.get(id=schedule_id).user
    print(user)

    print('Buscando o agendamento')
    # Verifica se o agendamento ainda é valido: 
    if not Schedule.objects.filter(id=schedule_id).exists():
        raise ValueError(f"Agendamento para {schedule_id} não encontrado.")
    print('Agendamento encontrado')
    print('Id do agendamento: ' + str(schedule_id))
        
    print('Buscando a cloud')
    # Busca a cloud
    cloud = VM.objects.get(instance_id=instance_id).cloud.cloud_type

    return user, cloud, instance_id


def start(schedule_id):
    try:
        schedule = Schedule.objects.get(id=schedule_id)

        if schedule.status == 'cancelled':
            print('Agendamento cancelado, não executando.')
            return {"status": "cancelled", "message": "Task cancelled"}

        user, cloud, instance_id = check_info(schedule_id)

        if cloud == 'OCI':
            # Busca o config file da OCI
            credentials = OCICredentials.objects.get(user=user)
            print('Credenciais encontradas')
            print(credentials)
            print('Iniciando a VM')

            # Chamada da função para iniciar a VM e capturar o status
            result = start_vm_oci(credentials, instance_id)
            if result['status'] == 200:
                return {"status": "success", "message": "VM started successfully", "vm_name": instance_id}
            else:
                return {"status": "failed", "message": "Failed to start VM", "vm_name": instance_id}

        elif cloud == 'AWS':
            # Busca o config file da AWS
            credentials = AWSCredentials.objects.get(user=user)
            print('Credenciais encontradas')
            print(credentials)

            # Chamada da função para iniciar a VM e capturar o status
            result = start_vm_aws(credentials, instance_id)
            if result['status'] == 200:
                return {"status": "success", "message": "VM started successfully", "vm_name": instance_id}
            else:
                return {"status": "failed", "message": "Failed to start VM", "vm_name": instance_id}

    except Exception as e:
        print(f'Erro ao buscar informações do agendamento: {str(e)}')
        return {"status": "error", "message": str(e)}




def start_vm_result(task):
    """
    Função hook para processar o resultado da tarefa start_vm_oci.
    """
    result = task.result

    if result["status"] == "success":
        print(f"VM {result['vm_name']} iniciada com sucesso.")
    elif result["status"] == "failed":
        print(f"Falha ao iniciar a VM {result['vm_name']}: {result['message']}")
    elif result["status"] == "cancelled":
        print(f"Tarefa cancelada para a VM {result['vm_name']}.")
    else:
        print(f"Erro na execução da tarefa: {result['message']}")


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

