from .models import CareUser,DefaultSchedule
from django.shortcuts import render
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm
from django.views.generic import CreateView, ListView, UpdateView,TemplateView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class CareuserListView(SuperUserRequiredMixin,ListView):
    model = CareUser
    template_name = "careuser/list.html"
    context_object_name = "careusers"
    ordering = ['pk']

class CareuserCreateView(SuperUserRequiredMixin,CreateView):
    model = CareUser
    form_class = CareUserForm
    template_name = "careuser/new.html"
    success_url = reverse_lazy('careusers:list')

class CareuserEditView(SuperUserRequiredMixin,UpdateView):
    model = CareUser
    form_class = CareUserForm
    template_name = "careuser/edit.html"
    success_url = reverse_lazy('careusers:list')

class DefscheduleListView(SuperUserRequiredMixin,ListView):
    model = DefaultSchedule
    template_name = "careuser/def_sche_list.html"
    context_object_name = "defschedules"
    ordering = ['pk']

class DefscheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
    template_name = "careuser/def_sche_new.html"
    success_url = reverse_lazy('careusers:def_sche_list')
"""
class DefscheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    template_name = "careuser/def_sche_edit.html"
    context_object_name = "defschedules"
    success_url = reverse_lazy('careusers:def_sche_list')
"""