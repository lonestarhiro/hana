from .models import Schedule
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','kaigo_point','shogai_point','def_sche_id','check_flg','comfirm_flg','created_by','created_at','updated_by')
