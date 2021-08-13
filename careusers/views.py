from .models import Careuser
from django.shortcuts import render
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareuserForm
from django.views.generic import CreateView, ListView, UpdateView,TemplateView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class CareuserListView(SuperUserRequiredMixin,ListView):
    model =Careuser
    template_name = "careuser/list.html"
    context_object_name = "careusers"
    ordering = ['pk']

class CareuserCreateView(SuperUserRequiredMixin,CreateView):
    model = Careuser
    form_class = CareuserForm
    template_name = "careuser/new.html"
    success_url = reverse_lazy('careusers:list')

class CareuserEditView(SuperUserRequiredMixin,UpdateView):
    model = Careuser
    form_class = CareuserForm
    template_name = "careuser/edit.html"
    success_url = reverse_lazy('careusers:list')