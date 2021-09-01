from .models import CareUser,DefaultSchedule,User,Service
from django import forms

class CareUserForm(forms.ModelForm):
    class Meta:
        model = CareUser
        fields = '__all__'

class DefscheduleForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        exclude =  ('careuser',)

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staffs"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["staffs"].queryset = User.objects.filter(is_active=True,kaigo=True)

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
        self.fields["staffs"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["staffs"].queryset = User.objects.filter(is_active=True,kaigo=True)
