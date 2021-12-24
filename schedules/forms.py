from .models import Schedule,Report
from careusers.models import CareUser
from staffs.models import User
from services.models import Service
from django import forms
from crispy_forms.helper import FormHelper

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','def_sche','careuser_check_level','staff_check_level','created_by','created_at','updated_by')

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
        self.fields["careuser"].queryset = CareUser.objects.all().filter(is_active=True).order_by('last_kana','first_kana')
        self.fields["staff1"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff2"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff3"].queryset = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff4"].queryset = User.objects.filter(is_active=True,kaigo=True)

        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('kind','time')
        mins = {0:0,5:5,10:10,15:15,20:20,25:25,30:30,35:35,40:40,45:45,50:50,55:55}

        self.fields['start_date'] = forms.SplitDateTimeField(label="日時",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('schedule','created_by','created_at','updated_by')

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False

        self.fields['service_in_date']  = forms.SplitDateTimeField(label="サービス開始時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
        self.fields['service_out_date'] = forms.SplitDateTimeField(label="サービス終了時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
