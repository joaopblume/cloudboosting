# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import OCICredentials

class OCICredentialsForm(forms.ModelForm):
    class Meta:
        model = OCICredentials
        fields = ['tenancy_ocid', 'user_ocid', 'fingerprint', 'private_key', 'region']
        widgets = {
            'private_key': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

