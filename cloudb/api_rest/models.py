from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt

class OCICredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenancy_ocid = encrypt(models.CharField(max_length=100))
    user_ocid = encrypt(models.CharField(max_length=100))
    fingerprint = encrypt(models.CharField(max_length=100))
    private_key = encrypt(models.TextField())
    # Adiciona vinhedo como default do region
    region = encrypt(models.CharField(max_length=50, default="sa-vinhedo-1"))
    # Outros campos conforme necessário

    def __str__(self):
        return f"Credenciais OCI de {self.user.username}"
    

class AWSCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_key = encrypt(models.CharField(max_length=100))
    secret_key = encrypt(models.CharField(max_length=100))

    def __str__(self):
        return f"Credenciais AWS de {self.user.username}"

class UserCloud(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cloud_type = models.CharField(max_length=50, choices=[('OCI', 'Oracle Cloud Infrastructure'), ('AWS', 'Amazon Web Services'), ('Azure', 'Microsoft Azure')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cloud_type}"


class VM(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vms')
    cloud = models.ForeignKey(UserCloud, on_delete=models.CASCADE, related_name='vms')
    instance_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)
    cpu_count = models.IntegerField()
    memory_gb = models.FloatField()
    lifecycle_state = models.CharField(max_length=50)
    compartment_name = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} ({self.instance_id})"
    

class InstanceSchedule(models.Model):
    instance_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=[('daily', 'Daily'), ('monthly', 'Monthly')])
    week_days = models.CharField(max_length=255, blank=True, null=True)
    specific_time = models.TimeField(blank=True, null=True)
    time_option = models.CharField(max_length=20, blank=True, null=True)  # Adicione esse campo
    interval = models.IntegerField(blank=True, null=True)  # Adicione esse campo
    interval_unit = models.CharField(max_length=20, blank=True, null=True)  # Adicione esse campo
    time_from = models.TimeField(blank=True, null=True)  # Adicione esse campo
    time_to = models.TimeField(blank=True, null=True)  # Adicione esse campo
    occurrence = models.CharField(max_length=20, blank=True, null=True)
    day_of_week = models.CharField(max_length=20, blank=True, null=True)  # Adicione esse campo
    calendar_day = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f"Schedule for {self.instance_id} by {self.user.username}"
    

class IntervalSchedule(models.Model):
    instance_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_from = models.TimeField()
    time_to = models.TimeField()

    def __str__(self):
        return f"Interval Schedule for {self.instance_id} by {self.user.username}"
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


