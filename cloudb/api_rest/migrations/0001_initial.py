# Generated by Django 5.1.3 on 2024-11-12 01:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CloudProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('nickname', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('cloud_provider', models.ManyToManyField(to='api_rest.cloudprovider')),
            ],
        ),
        migrations.CreateModel(
            name='VirtualMachine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=10)),
                ('cloud_provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_rest.cloudprovider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_rest.user')),
            ],
        ),
    ]