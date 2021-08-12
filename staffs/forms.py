from django import forms
from staffs.models import User
from django.contrib.auth.forms import UserCreationForm

class StaffForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','birthday','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','is_staff','is_active','is_superuser','tel','phone','shaho','join','biko',
        'kanri','jimu','caremane','servkan','kaigo','yougu','kango','kinou','seikatu','ishi',
        'riha','ope','ryouyou','jihakan','sidou','hoiku','jisou','driver','eiyou','tyouri','gengo','tyounou')

class NewStaffForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','birthday','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','password1','password2','tel','phone','shaho','join','biko',
        'kanri','jimu','caremane','servkan','kaigo','yougu','kango','kinou','seikatu','ishi',
        'riha','ope','ryouyou','jihakan','sidou','hoiku','jisou','driver','eiyou','tyouri','gengo','tyounou')