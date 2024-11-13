from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt

class OCICredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenancy_ocid = encrypt(models.CharField(max_length=100))
    user_ocid = encrypt(models.CharField(max_length=100))
    fingerprint = encrypt(models.CharField(max_length=100))
    private_key = encrypt(models.TextField())
    compartment_id = encrypt(models.CharField(max_length=100))

    def __str__(self):
        return f"Credenciais OCI de {self.user.username}"

# class CloudProvider(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name

# class User(models.Model):
#     nickname = models.CharField(max_length=30, primary_key=True)
#     password = models.CharField(max_length=30)
#     email = models.EmailField()
#     cloud_provider = models.ManyToManyField(CloudProvider)
#     def __str__(self):
#         return self.name

# class VirtualMachine(models.Model):
#     name = models.CharField(max_length=100)
#     status = models.CharField(max_length=10)
#     cloud_provider = models.ForeignKey(CloudProvider, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name


