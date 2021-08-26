from .models import Schedule
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude =  ('kaigo_point','shogai_point','from_default')