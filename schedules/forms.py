from .models import Schedule
from django import forms

class ScheduleCreateForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','kaigo_point','shogai_point','from_default','check_flg','comfirm_flg')

class ScheduleEditForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','kaigo_point','shogai_point','from_default','check_flg','comfirm_flg')