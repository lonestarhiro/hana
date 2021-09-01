from .models import Schedule
from staffs.models import User
from careusers.models import CareUser
from django.db.models import Q
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import ScheduleForm
from django.views.generic import CreateView,ListView,UpdateView,DeleteView
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

        #利用者の絞込み検索用リスト
        careuser_obj = CareUser.objects.all().filter(is_active=True).order_by('pk')
        context['careuser_obj'] = careuser_obj
        
        selected_careuser = self.request.GET.get('careuser')
        context['selected_careuser'] = ""
        if selected_careuser is not None:
            context['selected_careuser'] = int(selected_careuser)

        #スタッフの絞込み検索用リスト
        staff_obj = User.objects.all().filter(is_active=True,kaigo=True).order_by('pk')
        context['staff_obj'] = staff_obj

        selected_staff = self.request.GET.get('staff')
        context['selected_staff'] = ""
        if selected_staff is not None:
            context['selected_staff'] = int(selected_staff)


        return context
    
    def get_queryset(self, **kwargs):

        #表示期間
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
        condition_date = Q(start_date__range=[st,ed])

        #利用者絞込み
        condition_careuser = Q()
        search_careuser = self.request.GET.get('careuser',default=None)
        if search_careuser is not None:
            condition_careuser = Q(careuser=CareUser(pk=search_careuser))

        #スタッフ絞込み
        condition_staff = Q()
        search_staff = self.request.GET.get('staff',default=None)
        if search_staff is not None:
            condition_staff = Q(staff1=User(pk=search_staff))|Q(staff2=User(pk=search_staff))|Q(staff3=User(pk=search_staff))|Q(staff4=User(pk=search_staff))|\
                              Q(tr_staff1=User(pk=search_staff))|Q(tr_staff2=User(pk=search_staff))|Q(tr_staff3=User(pk=search_staff))|Q(tr_staff4=User(pk=search_staff))

        queryset = Schedule.objects.filter(condition_date,condition_careuser,condition_staff).order_by('start_date')
        return queryset


class ScheduleCreateView(StaffUserRequiredMixin,CreateView):
    model = Schedule
    form_class = ScheduleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #終了日時を追記
        endtime = self.object.start_date + datetime.timedelta(minutes = self.object.service.time)
        endtime = localtime(endtime)
        self.object.end_date = endtime
        #最終更新者を追記
        created_by= self.request.user
        self.object.created_by = created_by
        #利用者スケジュールの重複をチェックしcheck_flgを付与
        careuser_check =False
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=self.object.careuser),(Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime))).exclude(id = self.object.pk)
        print(careuser_duplicate_check_obj)
        if careuser_duplicate_check_obj.count() > 0 :
            careuser_check=True
        else:
            careuser_check=False
        #スタッフスケジュールの重複をチェックしcheck_flgを付与
        staff_obj=(self.object.staff1,self.object.staff2,self.object.staff3,self.object.staff4)
        staff_check =False
        for staff in staff_obj:
            if(staff != None):
                staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                            (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff))).exclude(id = self.object.pk)
                if staff_duplicate_check_obj.count() > 0 :
                    staff_check =True
        #上記のいずれかに該当すればtrueにする
        if careuser_check or staff_check:
            self.object.check_flg = True
        else:
            self.object.check_flg = False

        form.save()

        return super(ScheduleCreateView,self).form_valid(form)

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})

class ScheduleEditView(StaffUserRequiredMixin,UpdateView):
    model = Schedule
    form_class = ScheduleForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #終了日時を追記
        endtime = self.object.start_date + datetime.timedelta(minutes = self.object.service.time)
        endtime = localtime(endtime)
        self.object.end_date = endtime
        #最終更新者を追記
        created_by= self.request.user
        self.object.created_by = created_by
        #利用者スケジュールの重複をチェックしcheck_flgを付与
        careuser_check =False
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=self.object.careuser),(Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime))).exclude(id = self.object.pk)
        print(careuser_duplicate_check_obj)
        if careuser_duplicate_check_obj.count() > 0 :
            careuser_check=True
        else:
            careuser_check=False
        #スタッフスケジュールの重複をチェックしcheck_flgを付与
        staff_obj=(self.object.staff1,self.object.staff2,self.object.staff3,self.object.staff4)
        staff_check =False
        for staff in staff_obj:
            if(staff != None):
                staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                            (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff))).exclude(id = self.object.pk)
                if staff_duplicate_check_obj.count() > 0 :
                    staff_check =True
        #上記のいずれかに該当すればtrueにする
        if careuser_check or staff_check:
            self.object.check_flg = True
        else:
            self.object.check_flg = False

        form.save()

        return super(ScheduleEditView,self).form_valid(form)

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})

class ScheduleDeleteView(StaffUserRequiredMixin,DeleteView):
    model = Schedule
    template_name ="schedules\schedule_delete.html"

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})