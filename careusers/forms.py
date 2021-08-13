from django.forms.models import ModelForm
from .models import Careuser
from django import forms

class CareuserForm(forms.ModelForm):
    class Meta:
        model = Careuser
        fields = '__all__'