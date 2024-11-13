# utils.py

import oci
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError




def validar_credenciais(config):
    try:
        identity_client = oci.identity.IdentityClient(config)
        user = identity_client.get_user(config["user"]).data
        return True
    except Exception as e:
        print(f"Erro na validação das credenciais: {e}")
        return False
    
    
def create_oci_config(creds):
    config = {
        "user": creds.user_ocid,
        "key_content": creds.private_key,
        "fingerprint": creds.fingerprint,
        "tenancy": creds.tenancy_ocid,
        "region": creds.region,
    }
    return config


def get_all_compartments(identity_client, tenancy_id):
    compartments = []
    try:
        # Lista todos os compartimentos acessíveis no locatário
        response = oci.pagination.list_call_get_all_results(
            identity_client.list_compartments,
            compartment_id=tenancy_id,
            compartment_id_in_subtree=True,
            access_level="ACCESSIBLE",
            lifecycle_state="ACTIVE"
        )
        compartments = response.data
    except Exception as e:
        print(f"Erro ao buscar compartimentos: {e}")
    return compartments


def listar_instancias_oci(creds):
    config = create_oci_config(creds)
    compute_client = oci.core.ComputeClient(config)
    identity_client = oci.identity.IdentityClient(config)

    tenancy_id = creds.tenancy_ocid

    # Obter todos os compartimentos
    all_compartments = get_all_compartments(identity_client, tenancy_id)

    # Criar um dicionário para mapear IDs de compartimento para nomes
    compartment_map = {tenancy_id: 'root'}
    for compartment in all_compartments:
        compartment_map[compartment.id] = compartment.name

    # Incluir o compartimento raiz na lista
    compartments = [tenancy_id] + [compartment.id for compartment in all_compartments]

    instances = []
    for compartment_id in compartments:
        try:
            response = oci.pagination.list_call_get_all_results(
                compute_client.list_instances,
                compartment_id=compartment_id
            )
            for instance in response.data:
                # Adiciona o nome do compartimento ao objeto da instância
                instance.compartment_name = compartment_map.get(compartment_id, 'Unknown')
                instances.append(instance)
        except Exception as e:
            print(f"Erro ao listar instâncias no compartimento {compartment_id}: {e}")

    return instances

def validar_credenciais_aws(access_key, secret_key):
    try:
        client = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        client.get_caller_identity()  # Valida as credenciais
        return True
    except (NoCredentialsError, PartialCredentialsError):
        return False
    


def listar_instancias_aws(credentials):
    # Inicializar o cliente EC2 com as credenciais do usuário
    session = boto3.Session(
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        region_name='us-east-1'  # Certifique-se de que a região está configurada nas credenciais
    )
    
    ec2 = session.client('ec2')
    response = ec2.describe_instances()
    
    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append({
                'id': instance["InstanceId"],
                'display_name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                'lifecycle_state': instance["State"]["Name"].upper(),
            })
    
    return instances