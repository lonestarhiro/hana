from .models import Schedule
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude =  ('end_date','kaigo_point','shogai_point','from_default','check_flg','comfirm_flg')