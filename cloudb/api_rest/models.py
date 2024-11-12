from django.db import models



#Create your models here.

class CloudProvider(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    nickname = models.CharField(max_length=30, primary_key=True)
    password = models.CharField(max_length=30)
    email = models.EmailField()
    cloud_provider = models.ManyToManyField(CloudProvider)
    def __str__(self):
        return self.name

class VirtualMachine(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    cloud_provider = models.ForeignKey(CloudProvider, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


