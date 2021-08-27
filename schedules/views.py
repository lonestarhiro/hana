from .models import Schedule
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import ScheduleCreateForm,ScheduleEditForm
from django.views.generic import CreateView, ListView, UpdateView
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime


#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）

class ScheduleListView(StaffUserRequiredMixin,ListView):
    model = Schedule
    queryset = Schedule.objects.all().order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            context['day_start']= "later"
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
            context['day_start']= "month"

        next_month   = datetime.datetime(year,month,1) + relativedelta(months=1)
        before_month = datetime.datetime(year,month,1) - relativedelta(months=1)
        context['year'] = year
        context['month']= month
        context['next_year']    = next_month.year
        context['next_month']   = next_month.month
        context['before_year']  = before_month.year
        context['before_month'] = before_month.month

        return context
    
    def get_queryset(self, **kwargs):

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day

            st= datetime.datetime(year,month,day)
            ed= datetime.datetime(year,month,calendar.monthrange(year, month)[1])


        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')

            st= datetime.datetime(year,month,1)
            ed= datetime.datetime(year,month,calendar.monthrange(year, month)[1])
        
        st = make_aware(st)
        ed = make_aware(ed)
        queryset = Schedule.objects.filter(start_date__range=[st,ed]).order_by('start_date')

        return queryset


class ScheduleCreateView(StaffUserRequiredMixin,CreateView):
    model = Schedule
    form_class = ScheduleCreateForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # employeeフィールドはログインしているユーザ名とする
        endtime = self.object.start_date + datetime.timedelta(minutes = self.object.service.time)
        endtime = localtime(endtime)
        self.object.end_date = endtime
        form.save()

        return super(ScheduleCreateView,self).form_valid(form)

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})

class ScheduleEditView(StaffUserRequiredMixin,UpdateView):
    model = Schedule
    form_class = ScheduleEditForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # employeeフィールドはログインしているユーザ名とする
        endtime = self.object.start_date + datetime.timedelta(minutes = self.object.service.time)
        endtime = localtime(endtime)
        self.object.end_date = endtime
        form.save()

        return super(ScheduleEditView,self).form_valid(form)

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})