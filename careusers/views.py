from .models import CareUser,DefaultSchedule
from django.shortcuts import render
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm
from django.views.generic import CreateView, ListView, UpdateView,TemplateView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class CareuserListView(SuperUserRequiredMixin,ListView):
    model = CareUser
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
    context_object_name = "defschedules"
    ordering = ['pk']

class DefscheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
   
    def get_success_url(self):
        return reverse_lazy('careusers:list',kwargs="'pk':careuser.pk")

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context

"""
class DefscheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    context_object_name = "defschedules"
    success_url = reverse_lazy('careusers:def_sche_list')
"""