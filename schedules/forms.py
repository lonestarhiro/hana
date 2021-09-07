from .models import Schedule
from careusers.models import DefaultSchedule
from staffs.models import User
from services.models import Service
from django import forms

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','check_flg','comfirm_flg','created_by','created_at','updated_by')

    def __init__ (self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        """
        if(self.fields["def_sche"] is not None):
            self.fields["staff1"].queryset = self.fields["def_sche"].staffs.all()
            self.fields["staff2"].queryset = self.fields["def_sche"].staffs.all()
            self.fields["staff3"].queryset = self.fields["def_sche"].staffs.all()
            self.fields["staff4"].queryset = self.fields["def_sche"].staffs.all()
        else:
            self.fields["staff1"].queryset = User.objects.filter(is_active=True,kaigo=True)
            self.fields["staff2"].queryset = User.objects.filter(is_active=True,kaigo=True)
            self.fields["staff3"].queryset = User.objects.filter(is_active=True,kaigo=True)
            self.fields["staff4"].queryset = User.objects.filter(is_active=True,kaigo=True)
        """
        
        self.fields["staff1"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff2"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff3"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff4"].queryset = User.objects.filter(is_active=True,kaigo=True)

        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('kind','time')
        mins = {0:0,5:5,10:10,15:15,20:20,25:25,30:30,35:35,40:40,45:45,50:50,55:55}

        self.fields['start_date'] = forms.SplitDateTimeField(label="日時",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
        

