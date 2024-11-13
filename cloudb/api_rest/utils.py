# utils.py

import oci

def validar_credenciais(tenancy_ocid, user_ocid, fingerprint, private_key, compartment_id):
    try:
        config = {
            "user": user_ocid,
            "key_content": private_key,
            "fingerprint": fingerprint,
            "tenancy": tenancy_ocid,
            "region": "us-ashburn-1",  # Ajuste conforme necessário
        }
        identity = oci.identity.IdentityClient(config)
        identity.get_compartment(compartment_id)
        return True
    except Exception as e:
        print(e)
        return False