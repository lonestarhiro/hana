from .models import Schedule,Report,AddRequest
from careusers.models import CareUser
from staffs.models import User
from services.models import Service
from django import forms
from crispy_forms.helper import FormHelper
import datetime
from django.utils.timezone import make_aware
from django.db.models import Prefetch,Case, When, Value,PositiveSmallIntegerField

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ('end_date','def_sche','careuser_check_level','staff_check_level','created_by','created_at','updated_at')

    def __init__ (self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        #リストをふりがな付に変更
        from .views import furigana_index_list
        #careuser
        obj =furigana_index_list(CareUser.objects.all().filter(is_active=True).order_by('last_kana','first_kana'),"careusers")
        careuser_choice = []
        for cu in obj:
            careuser_choice.append((cu.pk,cu))
        self.fields["careuser"].choices = careuser_choice
        #staff
        obj = furigana_index_list(User.objects.filter(is_active=True,kaigo=True).order_by('-is_staff','last_kana','first_kana'),"staffs")
        staff_choice = []
        staff_choice.append(("","---------"))
        for st in obj:
            staff_choice.append((st.pk,st))

        self.fields["staff1"].choices    = staff_choice
        self.fields["staff2"].choices    = staff_choice
        self.fields["staff3"].choices    = staff_choice
        self.fields["staff4"].choices    = staff_choice
        self.fields["tr_staff1"].choices = staff_choice
        self.fields["tr_staff2"].choices = staff_choice
        self.fields["tr_staff3"].choices = staff_choice
        self.fields["tr_staff4"].choices = staff_choice        

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
        """

        odr_text = Case(
            When(title__startswith="身体", then=Value(0)),
            When(title__startswith="生活", then=Value(1)),
            When(title__startswith="家事", then=Value(2)),
            When(title__startswith="重度", then=Value(3)),
            When(title__startswith="通院", then=Value(4)),
            When(title__icontains="身有", then=Value(5)),
            When(title__icontains="身無", then=Value(6)),
            default=Value(9),
            output_field=PositiveSmallIntegerField()
        )
        self.fields['service'].queryset = Service.objects.annotate(odr_text=odr_text).filter(is_active=True).order_by('kind','odr_text','time')

        self.fields['start_date'] = forms.SplitDateTimeField(label="日時",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
    
    def clean(self):
        #更新の場合のみチェック
        if self.instance.pk:
            cleaned_data = super().clean()
            staff1  = self.cleaned_data.get('staff1')
            report_obj = Report.objects.get(schedule=self.instance.pk)
            if report_obj.careuser_confirmed and staff1==None:
                self.add_error('staff1','実績記録登録済みのため、担当スタッフ1を未選択にはできません。') 

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('email_sent_date','warnings','error_warn_allowed','error_code','schedule','created_by','created_at','updated_by')
        widgets = {
            'mix_reverse': forms.HiddenInput()
        }

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
            msg = '終了時間が開始時間がより前か同じです。'
            #self.add_error('service_in_date',msg)
            self.add_error('service_out_date',msg)

class AddRequestForm(forms.ModelForm):
    class Meta:
        model = AddRequest
        exclude = ('created_by','created_at','confirmed_by','confirmed_at')
        widgets = {
            'careuser_txt' : forms.TextInput(attrs={'placeholder': '伊丹　はな子'}),
            'service_txt'  : forms.TextInput(attrs={'placeholder': '介護保険 身体30'}),
        }

    def __init__ (self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['start_date'] = forms.SplitDateTimeField(label="日時",widget=forms.SplitDateTimeWidget(date_attrs={"type":"date"}, time_attrs={"type":"time"}))
