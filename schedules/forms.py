from .models import Schedule
from staffs.models import User
from services.models import Service
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','kaigo_point','shogai_point','def_sche_id','check_flg','comfirm_flg','created_by','created_at','updated_by')
    def __init__ (self, careuser=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staff1"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff2"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff3"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff4"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields['service'].queryset = Service.objects.order_by('kind','time')