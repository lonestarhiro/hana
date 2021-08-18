from django import forms
from staffs.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

class StaffForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','short_name','birthday','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','is_staff','is_active','is_superuser','tel','phone','shaho','join','biko',
        'kanri','jimu','caremane','servkan','kaigo','yougu','kango','kinou','seikatu','ishi',
        'riha','ope','ryouyou','jihakan','sidou','hoiku','jisou','driver','eiyou','tyouri','gengo','tyounou')
        widgets = {
            'password': forms.PasswordInput()
        }

class StaffFormEdit(UserChangeForm):
    class Meta:
        model = User
        fields = ('last_name','first_name','last_kana','first_kana','short_name','birthday','staff_no','postcode',
        'adr_ken','adr_siku','adr_tyou','adr_bld','email','is_staff','is_active','is_superuser','tel','phone','shaho','join','biko',
        'kanri','jimu','caremane','servkan','kaigo','yougu','kango','kinou','seikatu','ishi',
        'riha','ope','ryouyou','jihakan','sidou','hoiku','jisou','driver','eiyou','tyouri','gengo','tyounou')