from .models import Schedule
from django.shortcuts import get_object_or_404,render,redirect
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import ScheduleForm
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
import datetime


#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class ScheduleListView(SuperUserRequiredMixin,ListView):
    model = Schedule
    queryset = Schedule.objects.all().order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.kwargs.get('year',datetime.datetime.today().year)
        context['month']= self.kwargs.get('month',datetime.datetime.today().month)

        return context
    
    def get_queryset(self, **kwargs):

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day

            st= datetime.date(year,month,day)
            ed= datetime.date(year,month+1,1)- datetime.timedelta(days=1)


        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')

            st= datetime.date(year,month,1)
            ed= datetime.date(year,month+1,1)- datetime.timedelta(days=1)
        
        queryset = Schedule.objects.filter(date__range=[st,ed]).order_by('date')

        return queryset


class ScheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = Schedule
    form_class = ScheduleForm
    
    def get_success_url(self):
        year = self.object.date.year
        month = self.object.date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})

class ScheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = Schedule
    form_class = ScheduleForm

    def get_success_url(self):
        year = self.object.date.year
        month = self.object.date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})
