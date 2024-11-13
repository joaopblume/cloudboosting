# Generated by Django 5.1.3 on 2024-11-13 13:56

import django_cryptography.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0002_remove_virtualmachine_cloud_provider_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocicredentials',
            name='compartment_id',
        ),
        migrations.AddField(
            model_name='ocicredentials',
            name='region',
            field=django_cryptography.fields.encrypt(models.CharField(default='sa-vinhedo-1', max_length=50)),
        ),
    ]