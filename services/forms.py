from .models import Service
from django import forms

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
