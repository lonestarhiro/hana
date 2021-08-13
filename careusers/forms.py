from django.forms.models import ModelForm
from .models import CareUser
from django import forms

class CareUserForm(forms.ModelForm):
    class Meta:
        model = CareUser
        fields = '__all__'