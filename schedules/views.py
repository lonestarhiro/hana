from .models import Schedule,Report
from staffs.models import User
from careusers.models import CareUser
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django import forms
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin
from django.urls import reverse_lazy
from .forms import ScheduleForm,ReportForm
from django.views.generic import CreateView,ListView,UpdateView,DeleteView
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime


#以下ログイン済みのみ表示(urlsにて制限中)
#mixinにて記述
class ScheduleDailyListView(ListView):
    model = Schedule 
    template_name = "schedules/schedule_daily.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None or self.kwargs.get('day')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day
            context['disp_day']= "today_2days"

        else:
            year  = self.kwargs.get('year')
            month = self.kwargs.get('month')
            day   = self.kwargs.get('day')
            context['disp_day']= "day"

        next_day   = datetime.datetime(year,month,day) + datetime.timedelta(days=1)
        before_day = datetime.datetime(year,month,day) - datetime.timedelta(days=1)
        next_day   = make_aware(next_day)
        before_day = make_aware(before_day)

        context['year'] = year
        context['month']= month
        context['day']  = day
        context['next_day']   = next_day
        context['before_day'] = before_day


        now      = datetime.datetime.now()
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        now      = make_aware(now)
        tomorrow = make_aware(tomorrow)

        #現在時刻（reportボタン切り替え用）
        context['time_now'] = now

        context['today_flg']    = False
        context['tomorrow_flg'] = False
        if year == now.year and month==now.month and day==now.day:
            context['today_flg']  = True
        elif year == tomorrow.year and month==tomorrow.month and day==tomorrow.day:
            context['tomorrow_flg'] = True

        #スタッフの絞込み検索用リスト
        if self.request.user.is_staff:
            staff_obj = User.objects.all().filter(is_active=True,kaigo=True).order_by('pk')
            context['staff_obj'] = staff_obj

        #選択中のユーザー
        context['selected_staff'] = self.get_selected_user_obj()

        return context

    def get_queryset(self, **kwargs):

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None or self.kwargs.get('day')==None:
            #今日から明日のスケジュールを表示
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day

            st = datetime.datetime(year,month,day)
            ed = st + datetime.timedelta(days=2) - datetime.timedelta(seconds=1)
        else:
            #今日から明日のスケジュールを表示
            year  = self.kwargs.get('year')
            month = self.kwargs.get('month')
            day   = self.kwargs.get('day')

            st = datetime.datetime(year,month,day)
            ed = st + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

        st = make_aware(st)
        ed = make_aware(ed)
        condition_date  = Q(start_date__range=[st,ed])

        selected_user = self.get_selected_user_obj()
        condition_staff = (Q(staff1=selected_user)|Q(staff2=selected_user)|Q(staff3=selected_user)|Q(staff4=selected_user)|\
                           Q(tr_staff1=selected_user)|Q(tr_staff2=selected_user)|Q(tr_staff3=selected_user)|Q(tr_staff4=selected_user))
    
        queryset = Schedule.objects.select_related('careuser','report').all().filter(condition_date,condition_staff).order_by('start_date')
    
        return queryset

    def get_selected_user_obj(self):
        #管理権限のあるユーザーは選択制、ないユーザーには自己のスケジュールのみ表示
        if self.request.user.is_staff:
            get_staff = self.request.GET.get('staff')
            if get_staff != None:
                selected_user_obj = User.objects.get(pk=get_staff)
            else:
                selected_user_obj = self.request.user
        else:
            selected_user_obj = self.request.user
        
        return selected_user_obj

class ScheduleCalendarListView(MonthWithScheduleMixin,ListView):
    model = Schedule
    date_field = "start_date"
    template_name = "schedules/schedule_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)

        #スタッフの絞込み検索用リスト
        if self.request.user.is_staff:
            staff_obj = User.objects.all().filter(is_active=True,kaigo=True).order_by('pk')
            context['staff_obj'] = staff_obj

            selected_staff = self.request.GET.get('staff')
            
            if selected_staff is not None:
                context['selected_staff'] = User.objects.get(pk=int(selected_staff))
            else:
                context['selected_staff'] = None
        else:
            context['selected_staff'] = self.request.user

        return context

class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #print(schedule_data)
        pk = self.kwargs.get('pk')
        schedule_data = Report.objects.select_related('schedule').get(pk=int(pk))
        if schedule_data.service_in_date is None:
            form = ReportForm(initial={
            'service_in_date' : schedule_data.schedule.start_date,
                'service_out_date': schedule_data.schedule.end_date,
            })
            context['form'] = form
        context['schedule_data'] = schedule_data
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #最終更新者を追記
        self.object.created_by = self.request.user
        form.save()

        return super(ReportUpdateView,self).form_valid(form)

    def get_success_url(self):
        year  = self.object.service_in_date.year
        month = self.object.service_in_date.month
        day   = self.object.service_in_date.day
        return reverse_lazy('schedules:dailylist',kwargs={'year':year,'month':month,'day':day})
        #return reverse_lazy('schedules:todaylist')

#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）

class ScheduleListView(StaffUserRequiredMixin,ListView):
    model = Schedule
    queryset = Schedule.objects.all().order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            context['day_start']= "today"
        elif self.kwargs.get('day'):
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
            context['anker_day']= str(self.kwargs.get('day'))
            context['posted_day']= self.kwargs.get('day')
            context['day_start'] = "month"
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
            context['day_start'] = "month"

        next_month   = datetime.datetime(year,month,1) + relativedelta(months=1)
        before_month = datetime.datetime(year,month,1) - relativedelta(months=1)
        context['posted_year'] = year
        context['posted_month']= month
        context['next_month']    = next_month
        context['before_month']  = before_month

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
        context['selected_staff'] = self.get_selected_user_obj()
        
        return context
    
    def get_queryset(self, **kwargs):

        #表示期間
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day
            st= datetime.datetime(year,month,day)
            ed= datetime.datetime(year,month,calendar.monthrange(year, month)[1],23,59)

        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
            st= datetime.datetime(year,month,1)
            ed= datetime.datetime(year,month,calendar.monthrange(year, month)[1],23,59)
        
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
        search_staff = self.get_selected_user_obj()
        if search_staff is not None:
            #変数を上書き
            search_staff = self.get_selected_user_obj().pk
            condition_staff = Q(staff1=User(pk=search_staff))|Q(staff2=User(pk=search_staff))|Q(staff3=User(pk=search_staff))|Q(staff4=User(pk=search_staff))|\
                              Q(tr_staff1=User(pk=search_staff))|Q(tr_staff2=User(pk=search_staff))|Q(tr_staff3=User(pk=search_staff))|Q(tr_staff4=User(pk=search_staff))

        queryset = Schedule.objects.select_related('careuser','staff1','staff2','staff3','staff4').filter(condition_date,condition_careuser,condition_staff).order_by('start_date')
        return queryset

    def get_selected_user_obj(self):

        if self.request.user.is_staff:
            selected_staff = self.request.GET.get('staff')
            if selected_staff != None:
                selected_user_obj = User.objects.get(pk=int(selected_staff))
            else:
                selected_user_obj = None
        
        return selected_user_obj


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
        careuser_check_level = 0
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=self.object.careuser),(Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime))).exclude(id = self.object.pk)
        if careuser_duplicate_check_obj.count() > 0 :
            if careuser_check_level<3:
                careuser_check_level = 3
                #時間が重複しているレコードのcareuser_check_levelを更新する
                careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)

        #スタッフスケジュールの重複をチェックしcheck_flgを付与
        staff_obj=(self.object.staff1,self.object.staff2,self.object.staff3,self.object.staff4,self.object.tr_staff1,self.object.tr_staff2,self.object.tr_staff3,self.object.tr_staff4)
        staff_check_level = 0

        for index,staff in enumerate(staff_obj):
            
            if(staff is None):
                if(index < self.object.peoples):
                    if staff_check_level < 2:
                        staff_check_level = 2
            else:
                staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                            (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff))).exclude(id = self.object.pk)
                if staff_duplicate_check_obj.count() > 0 :
                    if staff_check_level < 3:
                        staff_check_level = 3
                        #時間が重複しているレコードのstaff_check_levelをまとめて更新する
                        staff_duplicate_check_obj.update(staff_check_level=staff_check_level)

        #チェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level = staff_check_level

        schedule = form.save()

        #実績記録reportレコードを作成
        Report.objects.create(schedule=schedule,created_by=self.request.user)

        return super(ScheduleCreateView,self).form_valid(form)

    def get_success_url(self):
        year  = self.object.start_date.year
        month = self.object.start_date.month
        day   = self.object.start_date.day
        return reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})
        #return reverse_lazy('schedules:thismonthlist')
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
      
        careuser_check_level= self.sche_update_careusers(self.object)
        staff_check_level = self.sche_update_staffs(self.object)

        #チェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level = staff_check_level

        form.save()
        return super(ScheduleEditView,self).form_valid(form)

    #利用者の時間重複しているレコードの更新
    def sche_update_careusers(self,object):

        #利用者スケジュールの重複をチェックしcheck_flgを付与
        careuser_check_level = 0
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=object.careuser),(Q(start_date__lte=object.start_date,end_date__gt=object.start_date) | Q(start_date__lt=object.end_date,end_date__gte=object.end_date))).exclude(id=object.pk)
        if careuser_duplicate_check_obj.count()>0:
            #変更レコードのオブジェクトに返す
            careuser_check_level = 3
            #時間が重複しているレコードのcareuser_check_levelをまとめて更新する
            careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)

        #更新前の時間情報を取得
        old_obj = Schedule.objects.get(id=object.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date

        #更新前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.all().filter(Q(careuser=object.careuser,careuser_check_level=3),(Q(start_date__lte=old_start_date,end_date__gt=old_start_date) | Q(start_date__lt=old_end_date,end_date__gte=old_end_date))).exclude(id=object.pk)

        for obj in error_obj:
            if (obj.start_date <= object.start_date and obj.end_date > object.start_date) or(obj.start_date < object.end_date and obj.end_date >= object.end_date):
                new_flg = 3
            else:
                new_flg = 0                          

            #エラー値を更新
            obj.careuser_check_level=new_flg
            obj.save()
        
        return careuser_check_level

    #スタッフの時間重複しているレコードの更新
    def sche_update_staffs(self,object):

        #追加後・変更後オブジェクトと同一スタッフ、時間が重複していないかチェックし、重複があれば重複レコードのフラグを変更し、staff_check_levelを返す
        check_staffs = (object.staff1,object.staff2,object.staff3,object.staff4,object.tr_staff1,object.tr_staff2,object.tr_staff3,object.tr_staff4)
        staff_check_level =0;

        
        for index,staff in enumerate(check_staffs):

            #必要人数以下の状態であれば、staff_check_levelに２を付与
            if(index < self.object.peoples):
                if staff is None:
                    if staff_check_level < 2:
                        staff_check_level = 2

            if staff is not None:
                #変更レコードのスタッフ毎にスタッフ、時間の重複をチェック
                error_object = Schedule.objects.all().filter((Q(start_date__lte=object.start_date,end_date__gt=object.start_date) | Q(start_date__lt=object.end_date,end_date__gte=object.end_date)),\
                                (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)|Q(tr_staff1=staff)|Q(tr_staff2=staff)|Q(tr_staff3=staff)|Q(tr_staff4=staff))).exclude(id = object.pk)
                #もし重複するレコードがあれば、他のレコードに重複フラグを付与
                if error_object.count():
                    #変更レコードのオブジェクトに返す
                    staff_check_level =3;
                    #他の重複しているレコードにフラグをまとめて付与
                    error_object.update(staff_check_level=staff_check_level)


        #変更前のデータにより重複していたレコードが、重複解消していればフラグを更新する。
        #変更前のデータを取得
        old_obj = Schedule.objects.get(id=object.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date
        old_check_staffs = (old_obj.staff1,old_obj.staff2,old_obj.staff3,old_obj.staff4,old_obj.tr_staff1,old_obj.tr_staff2,old_obj.tr_staff3,old_obj.tr_staff4)
        
        for index,staff in enumerate(old_check_staffs):
            if staff is not None:
                #変更前の情報により、重複していたレコードを取得
                old_error_object = Schedule.objects.all().filter((Q(start_date__lte=old_start_date,end_date__gt=old_start_date) | Q(start_date__lt=old_end_date,end_date__gte=old_end_date)),\
                                (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)|Q(tr_staff1=staff)|Q(tr_staff2=staff)|Q(tr_staff3=staff)|Q(tr_staff4=staff))).exclude(id=object.pk)
                if old_error_object.count()>0:
                    for obj in old_error_object:
                        #今回の更新で重複が解消されていればフラグを更新する。
                        clear_flg=True
                        no_staff_check = False;
                        for index,stf in enumerate(check_staffs):
                            if(index < obj.peoples):
                                if stf is None:
                                    no_staff_check = True;
                            if stf is not None:
                                if ((obj.start_date <= object.start_date and obj.end_date > object.start_date) or (obj.start_date < object.end_date and obj.end_date >= object.end_date))\
                                and ((obj.staff1==stf) or (obj.staff2==stf) or (obj.staff3==stf) or (obj.staff4==stf) or (obj.tr_staff1==stf) or (obj.tr_staff2==stf) or (obj.tr_staff3==stf) or (obj.tr_staff4==stf)):
                                    clear_flg=False
                                    break
                        print(1,obj,str(clear_flg))
                        #調査しているレコードが他のレコードと重複していないかチェック
                        recheck_staffs = (obj.staff1,obj.staff2,obj.staff3,obj.staff4,obj.tr_staff1,obj.tr_staff2,obj.tr_staff3,obj.tr_staff4)
                        for stf in recheck_staffs:
                            if stf is not None:
                                recheck_obj = Schedule.objects.all().filter((Q(start_date__lte=obj.start_date,end_date__gt=obj.start_date) | Q(start_date__lt=obj.end_date,end_date__gte=obj.end_date)),\
                                    (Q(staff1=stf)|Q(staff2=stf)|Q(staff3=stf)|Q(staff4=stf)|Q(tr_staff1=stf)|Q(tr_staff2=stf)|Q(tr_staff3=stf)|Q(tr_staff4=stf))).exclude(id = object.pk).exclude(id = obj.pk)
                                if recheck_obj.count()>0:
                                    clear_flg=False
                        print(2,obj,str(clear_flg))
                        if clear_flg:
                            #必要人数がセットされていなければ2を、されていれば0をセット
                            if no_staff_check:
                                new_flg=2
                            else:
                                new_flg=0
                            obj.staff_check_level = staff_check_level
                            obj.save()
        return staff_check_level           

    def get_success_url(self):
        year  = self.object.start_date.year
        month = self.object.start_date.month
        day   = self.object.start_date.day
        return reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})
        #return reverse_lazy('schedules:thismonthlist')

class ScheduleDeleteView(StaffUserRequiredMixin,DeleteView):
    model = Schedule
    template_name ="schedules\schedule_delete.html"

    def delete(self, request, *args, **kwargs):

        del_obj = self.get_object()

        #更新前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.all().filter(Q(careuser=del_obj.careuser,careuser_check_level=3),(Q(start_date__lte=del_obj.start_date,end_date__gt=del_obj.start_date) | Q(start_date__lt=del_obj.end_date,end_date__gte=del_obj.end_date))).exclude(id = del_obj.pk)

        for obj in error_obj:
            sametime_check = Schedule.objects.all().filter(Q(careuser=obj.careuser,careuser_check_level=3),(Q(start_date__lte=obj.start_date,end_date__gt=obj.start_date) | Q(start_date__lt=obj.end_date,end_date__gte=obj.end_date))).exclude(id = del_obj.pk).exclude(id = obj.pk)
            if sametime_check.count()>0:
                careuser_check_level = 3
            else:
                careuser_check_level = 0                          

            #エラー値を更新
            obj.careuser_check_level=careuser_check_level
            obj.save()


        #削除前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.all().filter(Q(staff_check_level=3),(Q(start_date__lte=del_obj.start_date,end_date__gt=del_obj.start_date) | Q(start_date__lt=del_obj.end_date,end_date__gte=del_obj.end_date))).exclude(id = del_obj.pk)

        #今回の削除で解消される場合はエラーを削除する
        for obj in error_obj:
            renew_staff_check_level=0;
            check_staffs_obj = (obj.staff1,obj.staff2,obj.staff3,obj.staff4,obj.tr_staff1,obj.tr_staff2,obj.tr_staff3,obj.tr_staff4)
            #削除されるレコードとエラーレコードを比較
            for index,stf in enumerate(check_staffs_obj):
                #エラーレコードのスタッフ選択状況
                if(stf is None):
                    if(index < obj.peoples):
                        if(renew_staff_check_level<2):
                            renew_staff_check_level = 2
                else:
                    #エラーレコードが削除レコード以外のレコードと時間、スタッフが重複していないかチェック
                    recheck_obj= Schedule.objects.all().filter((Q(start_date__lte=obj.start_date,end_date__gt=obj.start_date) | Q(start_date__lt=obj.end_date,end_date__gte=obj.end_date)),\
                                    (Q(staff1=stf)|Q(staff2=stf)|Q(staff3=stf)|Q(staff4=stf)|Q(tr_staff1=stf)|Q(tr_staff2=stf)|Q(tr_staff3=stf)|Q(tr_staff4=stf))).exclude(id=del_obj.pk).exclude(id=obj.pk)
                    if recheck_obj.count()>0:
                        if renew_staff_check_level<3:
                            renew_staff_check_level=3

            #エラー値を更新
            obj.staff_check_level=renew_staff_check_level
            obj.save()
  
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})