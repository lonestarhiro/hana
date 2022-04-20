from django import forms
from staffs.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
import datetime

class StaffForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','short_name','birthday','salary','pay_bike','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','is_staff','is_active','is_superuser','tel','phone','shaho','join','biko',
        'servkan','kaigo','jimu','caremane','sousien','servsou','kaifuku','jitumu','shonin',"kisoken",'helper2','doukou')
        year = int(datetime.datetime.now().strftime('%Y'))+1
        widgets = {
            'password': forms.PasswordInput(),
            'birthday': forms.SelectDateWidget(years=[x for x in range(1910,year)]),
            'join': forms.SelectDateWidget(years=[x for x in range(year-15,year)]),
        }

class StaffFormEdit(UserChangeForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','short_name','birthday','salary','pay_bike','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','is_staff','is_active','is_superuser','tel','phone','shaho','join','biko',
        'servkan','kaigo','jimu','caremane','sousien','servsou','kaifuku','jitumu','shonin',"kisoken",'helper2','doukou')
        year = int(datetime.datetime.now().strftime('%Y'))+1
        widgets = {
            'birthday': forms.SelectDateWidget(years=[x for x in range(1910,year)]),
            'join': forms.SelectDateWidget(years=[x for x in range(year-15,year)]),
        }