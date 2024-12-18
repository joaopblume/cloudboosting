from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from api_rest.views import *
import json
from api_rest.models import *
from unittest.mock import patch
from api_rest.utils import validar_credenciais



# Testing URLS

class TestUrls(SimpleTestCase):
    def test_login_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_view)

    def test_home_resolves(self):
        url = reverse('user_home')
        self.assertEquals(resolve(url).func, user_home)

    def test_register_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, register)

    def test_register_cloud_resolves(self):
        url = reverse('register_cloud')
        self.assertEquals(resolve(url).func, register_cloud)

    def test_cloud_credentials_resolves(self):
        url = reverse('cloud_credentials', args=['oci'])
        self.assertEquals(resolve(url).func, cloud_credentials)

    def test_oci_credentials_resolves(self):
        url = reverse('oci_credentials')
        self.assertEquals(resolve(url).func, oci_credentials_view)

    def test_aws_credentials_resolves(self):
        url = reverse('aws_credentials')
        self.assertEquals(resolve(url).func, aws_credentials_view)

    def test_list_instances_resolves(self):
        url = reverse('listar_instancias_cloud', args=[1])
        self.assertEquals(resolve(url).func, listar_instancias_cloud)

    def test_agendar_vm_resolves(self):
        url = reverse('agendar_vm', args=['instance_id'])
        self.assertEquals(resolve(url).func, agendar_vm)

    def test_listar_agendamentos_resolves(self):
        url = reverse('listar_agendamentos', args=['instance_id'])
        self.assertEquals(resolve(url).func, listar_agendamentos)

    def test_edit_schedule_resolves(self):
        url = reverse('alterar_agendamento', args=[1])
        self.assertEquals(resolve(url).func, alterar_agendamento)

# Testing Views

class TestViews(TestCase):
    def setUp(self):
        # Cria um usuário de teste
        self.user = User.objects.create_user(
            username='joao',
            password='Joaozinho05!'
        )

        self.user_cloud = UserCloud.objects.create(
            user=self.user,
            cloud_type='OCI'
        )

        self.oci_credentials = OCICredentials.objects.create(
            user=self.user,
            tenancy_ocid='ocid1.tenancy.oc1..aaaaaaaabbbbbb',
            user_ocid='ocid1.user.oc1..aaaaaaaabbbbbb',
            fingerprint='aa:bb:cc:dd:ee:ff:gg:hh:ii:jj:kk:ll:mm:nn:oo:pp:qq:rr:ss:tt',
            private_key='-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDd6V1HvXuX\n...',
            region='sa-vinhedo-1'
        )

    def test_login_view_GET(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_view_GET(self):
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_home_view_GET(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('user_home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_home.html')

    def test_register_cloud_view_GET(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('register_cloud'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_cloud.html')

    def test_cloud_credentials_view_GET(self):
        self.client.force_login(self.user)

        # Teste para AWS (redireciona para 'aws_credentials')
        response = self.client.get(reverse('cloud_credentials', args=['aws']))
        self.assertEquals(response.status_code, 302)  # Verifica se é redirecionamento
        self.assertRedirects(response, reverse('aws_credentials'))  # Verifica o destino do redirecionamento


    def test_oci_credentials_view_GET(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('oci_credentials'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'oci_credentials_form.html')

    def test_aws_credentials_view_GET(self):

        response = self.client.get(reverse('aws_credentials'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'aws_credentials_form.html')

    '''
    EXEMPLE FOR TESTING CREDENTIALS FORM -> POST

    @patch('api_rest.views.validar_credenciais') 
    def test_cloud_credentials_view_GET(self, mock_validate):
        self.client.force_login(self.user)
        mock_validate.return_value = True

        response = self.client.get(reverse('oci_credentials'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'oci_credentials.html')

        # Verifica se a função foi chamada com os dados esperados
        mock_validate.assert_called_once_with({
            "tenancy": self.oci_credentials.tenancy_ocid,
            "user": self.oci_credentials.user_ocid,
            "fingerprint": self.oci_credentials.fingerprint,
            "private_key": self.oci_credentials.private_key,
            "region": self.oci_credentials.region,
        })
        '''