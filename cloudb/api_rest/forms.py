from django import forms

from .models import OCICredentials
from .models import AWSCredentials

class OCICredentialsForm(forms.ModelForm):
    class Meta:
        model = OCICredentials
        fields = ['tenancy_ocid', 'user_ocid', 'fingerprint', 'private_key', 'region']
        widgets = {
            'private_key': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }


class AWSCredentialsForm(forms.ModelForm):
    class Meta:
            model = AWSCredentials
            fields = ['access_key', 'secret_key']
