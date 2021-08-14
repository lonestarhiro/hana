from .models import CareUser,DefaultSchedule
from django.shortcuts import render
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm
from django.views.generic import CreateView, ListView, UpdateView,DetailView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class CareuserListView(SuperUserRequiredMixin,ListView):
    model = CareUser
    queryset = CareUser.objects.all().prefetch_related("defaultschedule_set").all()
    ordering = ['pk']

class CareuserCreateView(SuperUserRequiredMixin,CreateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class CareuserEditView(SuperUserRequiredMixin,UpdateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleListView(SuperUserRequiredMixin,ListView):
    model = DefaultSchedule
    ordering = ['pk']

    def get_queryset(self):
        careuser_id = self.kwargs['careuser_id']
        return self.model.objects.filter(careuser_id=careuser_id)
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DefscheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
    """
    def get_form_kwargs(self):
        kwargs = super(DefscheduleCreateView,self).get_form_kwargs()
        kwargs['careuser_id'] = self.request.careuser_id
        print(kwargs)
        return kwargs
    """
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    form_class = DefscheduleForm

    def get_success_url(self):
        return reverse_lazy('careusers:list')
