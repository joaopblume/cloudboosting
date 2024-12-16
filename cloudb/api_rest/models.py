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
    

class Schedule(models.Model):
    instance_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
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
        return f"Schedule for {self.user} on {self.instance} (Next: {self.next_execution})"
    
    
class WeeklySchedule(models.Model):
    """
    Represents weekly schedules with specific days and time intervals.
    """
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='weekly_schedules')
    day_of_week = models.CharField(
        max_length=9,
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ]
    )
    time_interval_start = models.TimeField()
    time_interval_end = models.TimeField()

    def __str__(self):
        return f"Weekly: {self.day_of_week} ({self.time_interval_start} - {self.time_interval_end})"



class MonthlySchedule(models.Model):
    """
    Represents monthly schedules with specific days and time intervals.
    """
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='monthly_schedules')
    day_of_month = models.PositiveIntegerField()
    time_interval_start = models.TimeField()
    time_interval_end = models.TimeField()

    def __str__(self):
        return f"Monthly: Day {self.day_of_month} ({self.time_interval_start} - {self.time_interval_end})"
    
class CombinedScheduleView(models.Model):
    schedule_id = models.IntegerField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    instance_id = models.CharField(max_length=255)
    instance_name = models.CharField(max_length=255)
    schedule_created_at = models.DateTimeField()
    weekly_day = models.CharField(max_length=9, null=True, blank=True)
    weekly_start = models.TimeField(null=True, blank=True)
    weekly_end = models.TimeField(null=True, blank=True)
    monthly_day = models.PositiveIntegerField(null=True, blank=True)
    monthly_start = models.TimeField(null=True, blank=True)
    monthly_end = models.TimeField(null=True, blank=True)

    class Meta:
        managed = False  # Django não gerencia esta tabela
        db_table = 'combined_schedule_view'  # Nome da view no banco de dados

    def __str__(self):
        return f"Schedule ID: {self.schedule_id}, Instance: {self.instance_name}, User: {self.user_name}"