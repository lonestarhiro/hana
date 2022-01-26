from .models import Schedule,Report
from careusers.models import CareUser
from staffs.models import User
from services.models import Service
from django import forms
from crispy_forms.helper import FormHelper
from datetime import datetime
from django.utils.timezone import make_aware

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','def_sche','careuser_check_level','staff_check_level','created_by','created_at','updated_by')

    def __init__ (self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        """
        if(self.fields["def_sche"]):
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
        staff_query = User.objects.filter(is_active=True,kaigo=True)
        self.fields["staff1"].queryset    = staff_query
        self.fields["staff2"].queryset    = staff_query
        self.fields["staff3"].queryset    = staff_query
        self.fields["staff4"].queryset    = staff_query
        self.fields["tr_staff1"].queryset = staff_query
        self.fields["tr_staff2"].queryset = staff_query
        self.fields["tr_staff3"].queryset = staff_query
        self.fields["tr_staff4"].queryset = staff_query

        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('kind','time')
        mins = {0:0,5:5,10:10,15:15,20:20,25:25,30:30,35:35,40:40,45:45,50:50,55:55}

        self.fields['start_date'] = forms.SplitDateTimeField(label="日時",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
    
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('error_code','schedule','created_by','created_at','updated_by')

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False

        self.fields['service_in_date']  = forms.SplitDateTimeField(label="サービス開始時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
        self.fields['service_out_date'] = forms.SplitDateTimeField(label="サービス終了時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
    """
    def clean_service_in_date(self):
        service_in_date  = self.cleaned_data.get('service_in_date')
        #service_out_date  = self.cleaned_data.get('service_out_date')#なぜか取れない
        time_now = make_aware(datetime.now())
        #print(service_in_date)
        #print(service_out_date)#なぜか取れない
        if service_in_date > time_now:
            self.add_error('service_in_date','開始時間が現在より先です。予定時刻が変更された場合は担当スタッフまで修正をご依頼下さい。') 
        return service_in_date
    
    def clean_service_out_date(self):
        service_in_date  = self.cleaned_data.get('service_in_date')
        service_out_date = self.cleaned_data.get('service_out_date')
        #print(service_in_date)
        #print(service_out_date)
        if service_in_date > service_out_date:
            self.add_error('service_in_date','終了時間が開始時間がより前です。入力を確認してください。')
            self.add_error('service_out_date','終了時間が開始時間がより前です。入力を確認してください。') 
        return service_out_date
    
    def clean_in_time_main(self):
        in_time_main = self.cleaned_data.get('in_time_mian')
        #print(self.instance.pk)
        self.add_error('in_time_main','a')
        return in_time_main
    
    def clean_biko(self):
        biko  = self.cleaned_data.get('service_biko')
        print(biko)
        #print(service_out_date)#なぜか取れない
        if biko is None:
            self.add_error('biko','備考欄への入力は必須です。')
        else:
            self.add_error('biko',None)
        return biko
    """