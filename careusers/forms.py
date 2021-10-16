from .models import CareUser,DefaultSchedule,User,Service
from django import forms
import datetime

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
        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('kind','time')

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
        self.fields['service'].queryset = Service.objects.filter(is_active=True).order_by('kind','time')
