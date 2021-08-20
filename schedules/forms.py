from .models import Schedule
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude =  ('from_default',)