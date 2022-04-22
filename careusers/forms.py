from .models import CareUser,DefaultSchedule,User,Service
from django import forms
import datetime
from django.db.models import Case, When, Value,PositiveSmallIntegerField

class CareUserForm(forms.ModelForm):
    class Meta:
        model = CareUser
        fields = '__all__'
        year = int(datetime.datetime.now().strftime('%Y'))+1
        widgets = {
            'birthday': forms.SelectDateWidget(years=[x for x in range(1910,year)]),
            'startdate': forms.SelectDateWidget(years=[x for x in range(year-15,year)])
        }

class DefscheduleForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        exclude =  ('careuser',)

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

class DefscheduleNewForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        fields = '__all__'
        widgets = {
            'careuser': forms.HiddenInput()
        }
    
    def __init__ (self, careuser=None, *args, **kwargs):
        if careuser != None:
            self.base_fields["careuser"].initial = careuser
        super().__init__(*args, **kwargs)
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

