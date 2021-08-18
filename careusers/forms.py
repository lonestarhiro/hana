from .models import CareUser,DefaultSchedule,User
from django import forms

class CareUserForm(forms.ModelForm):
    class Meta:
        model = CareUser
        fields = '__all__'

class DefscheduleForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        exclude =  ('careuser',)
        #widgets = {
        #    'staffs': forms.CheckboxSelectMultiple
        #}
    def __init__ (self, *args, **kwargs):
        super(DefscheduleForm, self).__init__(*args, **kwargs)
        self.fields["staffs"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["staffs"].queryset = User.objects.filter(is_active=True)

class DefscheduleNewForm(forms.ModelForm):
    class Meta:
        model = DefaultSchedule
        fields = "__all__"
    
    def __init__ (self, *args, **kwargs):
        super(DefscheduleNewForm, self).__init__(*args, **kwargs)
        self.fields["staffs"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["staffs"].queryset = User.objects.filter(is_active=True)
