from django.forms.models import ModelForm
from .models import CareUser,DefaultSchedule
from django import forms

class CareUserForm(forms.ModelForm):
    class Meta:
        model = CareUser
        fields = '__all__'

class DefscheduleForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        exclude =  ('careuser',)