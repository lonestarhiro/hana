from asyncio.windows_events import NULL
from .models import Schedule,Report
from careusers.models import CareUser
from staffs.models import User
from services.models import Service
from django import forms
from crispy_forms.helper import FormHelper
import datetime
from django.utils.timezone import make_aware
from django.db.models import Prefetch

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
        exclude = ('mix_reverce','communicate','error_code','schedule','created_by','created_at','updated_by')

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False

        self.fields['service_in_date']  = forms.SplitDateTimeField(label="サービス開始時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
        self.fields['service_out_date'] = forms.SplitDateTimeField(label="サービス終了時間",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
        self.fields['biko'].required = True

        check_obj = Report.objects.prefetch_related(Prefetch("schedule",queryset=Schedule.objects.select_related('service'))).get(pk=self.instance.pk)
        #身体・生活等複合の場合
        if check_obj.schedule.service.mix_items:
            self.fields['in_time_main'].required = True
            self.fields['in_time_sub'].required = True
        #移動時の行先が必要な場合
        if check_obj.schedule.service.destination:
            self.fields['destination'].required = True
    
    
    #フィールドは単一のデータポイントであり(取得順あり)、フォームはフィールドの集まりです。
    """
    def clean_service_in_date(self):
        service_in_date  = self.cleaned_data.get('service_in_date')
        time_now = make_aware(datetime.datetime.now())
        if service_in_date > time_now:
            self.add_error('service_in_date','開始時間が現在時刻より先です。予定時刻が変更された場合は担当スタッフまで修正をご依頼下さい。') 
        return service_in_date
    
    #全体のクリーンは個別をpassしたデータのみ渡される?
    #絶対に受付できない事項のみ記載。受付可能なチェックはjavascriptにてバリデーションする。
    def clean(self):
        cleaned_data = super().clean()
        service_in_date  = cleaned_data.get('service_in_date')
        service_out_date = cleaned_data.get('service_out_date')

        #内訳時間のチェック
        if cleaned_data.get('in_time_main'):
            in_time_main = cleaned_data.get('in_time_main')
            in_time_sub = cleaned_data.get('in_time_sub')

            in_time_total = in_time_main + in_time_sub
            end_for_check = service_in_date + datetime.timedelta(minutes=in_time_total)
            if not end_for_check == service_out_date:
                msg= "内訳時間の合計時間が終了時間に合いません。"
                self.add_error('in_time_main',msg)
                self.add_error('in_time_sub',msg)
        #開始時刻と終了時刻の関係
        if service_in_date >= service_out_date:
            msg = '終了時間が開始時間がより前か同じです。入力を確認してください。'
            #self.add_error('service_in_date',msg)
            self.add_error('service_out_date',msg)
    """