from .models import Schedule
from django.shortcuts import get_object_or_404,render,redirect
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import ScheduleForm
from django.views.generic import CreateView, ListView, UpdateView,DeleteView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class ScheduleListView(SuperUserRequiredMixin,ListView):
    model = Schedule
    queryset = Schedule.objects.all().order_by('date')

class ScheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = Schedule
    form_class = ScheduleForm
    
    def get_success_url(self):
        return reverse_lazy('schedules:list')

class ScheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = Schedule
    form_class = ScheduleForm
    
    def get_success_url(self):
        return reverse_lazy('schedules:list')
