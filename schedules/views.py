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
                        #時間が重複しているレコードのstaff_check_levelを更新する
                        staff_duplicate_check_obj.update(staff_check_level=staff_check_level)

        #チェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level = staff_check_level

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
        careuser_check_level = 0
        careuser_duplicate_check_obj = Schedule.objects.filter(Q(careuser=self.object.careuser),(Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime))).exclude(id = self.object.pk)
        if careuser_duplicate_check_obj.count() > 0 :
            careuser_check_level = 3
            #時間が重複しているレコードのcareuser_check_levelを更新する
            careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)

        #既にあるスタッフスケジュールとの重複をチェックしcheck_flgを付与
        staff_obj=(self.object.staff1,self.object.staff2,self.object.staff3,self.object.staff4,self.object.tr_staff1,self.object.tr_staff2,self.object.tr_staff3,self.object.tr_staff4)
        staff_check_level = 0

        for index,staff in enumerate(staff_obj):
            
            if(staff is None):
                if(index < self.object.peoples):
                    if staff_check_level < 2:
                        staff_check_level = 2
            else:
                staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                            (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)|Q(tr_staff1=staff)|Q(tr_staff2=staff)|Q(tr_staff3=staff)|Q(tr_staff4=staff))).exclude(id = self.object.pk)
                if staff_duplicate_check_obj.count() > 0 :
                    staff_check_level = 3
                    #時間が重複しているレコードのstaff_check_levelを更新する
                    staff_duplicate_check_obj.update(staff_check_level=staff_check_level)

        
        #更新前の時間と重複しエラーが出ているレコードのエラーを解除
        old_obj = Schedule.objects.get(id=self.object.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date

        #更新前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.all().filter(Q(staff_check_level=3),(Q(start_date__lte=old_start_date,end_date__gt=old_start_date) | Q(start_date__lt=old_end_date,end_date__gte=old_end_date))).exclude(id = self.object.pk)

        #今回の更新で解消される場合はエラーを削除する
        for obj in error_obj:
            for index,stf in enumerate(staff_obj):
                renew_staff_check_level=0;
                if(stf is None):
                    if(index < obj.peoples):
                        if(renew_staff_check_level<2):
                            renew_staff_check_level = 2
                else:
                    if (obj.start_date <= self.object.start_date and obj.end_date > self.object.start_date) or(obj.start_date < endtime and obj.end_date >= endtime)\
                        and ((obj.staff1==stf) or (obj.staff2==stf) or(obj.staff3==stf) or(obj.staff4==stf) or(obj.tr_staff1==stf) or(obj.tr_staff2==stf) or(obj.tr_staff3==stf) or(obj.tr_staff4==stf)):
                
                        if renew_staff_check_level<3:
                            renew_staff_check_level=3 
                    #エラーが出ているレコードが更新レコード以外のレコードと重複していないかチェック
                    else:
                        recheck_staff = (obj.staff1,obj.staff2,obj.staff3,obj.staff4,obj.tr_staff1,obj.tr_staff2,obj.tr_staff3,obj.tr_staff4)
                        for re_staff in recheck_staff:
                            recheck_obj= Schedule.objects.all().filter((Q(start_date__lte=obj.start_date,end_date__gt=obj.start_date) | Q(start_date__lt=obj.end_date,end_date__gte=obj.end_date)),\
                                        (Q(staff1=re_staff)|Q(staff2=re_staff)|Q(staff3=re_staff)|Q(staff4=re_staff)|Q(tr_staff1=re_staff)|Q(tr_staff2=re_staff)|Q(tr_staff3=re_staff)|Q(tr_staff4=re_staff))).exclude(id = self.object.pk).exclude(id=obj.pk)
                            if recheck_obj.count()>0:
                                if renew_staff_check_level<3:
                                    renew_staff_check_level=3

            #エラー値を更新
            obj.staff_check_level=renew_staff_check_level
            obj.save()

        """
        old_staffs_obj = (old_obj.staff1,old_obj.staff2,old_obj.staff3,old_obj.staff4,old_obj.tr_staff1,old_obj.tr_staff2,old_obj.tr_staff3,old_obj.tr_staff4)

        #更新前のデータと同時間帯でエラーが出ているレコードを取得
        for staff in old_staffs_obj:
            error_obj= Schedule.objects.all().filter(Q(staff_check_level=3),(Q(start_date__lte=old_start_date,end_date__gt=old_start_date) | Q(start_date__lt=old_end_date,end_date__gte=old_end_date))).exclude(id = self.object.pk)

            #今回の更新で解消される場合はエラーを削除する
            for obj in error_obj:
                renew_staff_check_level=0;
                for index,stf in enumerate(staffs_obj):
                    if(stf is None):
                        if(index < obj.peoples):
                            if(renew_staff_check_level<2):
                                renew_staff_check_level = 2
                    else:

                        if (obj.start_date <= self.object.start_date and obj.end_date > self.object.start_date) or(obj.start_date < endtime and obj.end_date >= endtime)\
                            and ((obj.staff1==stf) or (obj.staff2==stf) or(obj.staff3==stf) or(obj.staff4==stf) or(obj.tr_staff1==stf) or(obj.tr_staff2==stf) or(obj.tr_staff3==stf) or(obj.tr_staff4==stf)):
                
                           #rst = obj.filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                           #                 (Q(staff1=stf)|Q(staff2=stf)|Q(staff3=s tf)|Q(staff4=stf)|Q(tr_staff1=stf)|Q(tr_staff2=stf)|Q(tr_staff3=stf)|Q(tr_staff4=stf))).exclude(id = self.object.pk)

                            if renew_staff_check_level<3:
                                renew_staff_check_level=3 
                        #エラーが出ているレコードが更新レコード以外のレコードと重複していないかチェック
                        else:
                            recheck_staff = (obj.staff1,obj.staff2,obj.staff3,obj.staff4,obj.tr_staff1,obj.tr_staff2,obj.tr_staff3,obj.tr_staff4)
                            for re_staff in recheck_staff:
                                recheck_obj= Schedule.objects.all().filter((Q(start_date__lte=obj.start_date,end_date__gt=obj.start_date) | Q(start_date__lt=obj.end_date,end_date__gte=obj.end_date)),\
                                            (Q(staff1=re_staff)|Q(staff2=re_staff)|Q(staff3=re_staff)|Q(staff4=re_staff)|Q(tr_staff1=re_staff)|Q(tr_staff2=re_staff)|Q(tr_staff3=re_staff)|Q(tr_staff4=re_staff))).exclude(id = self.object.pk).exclude(id=obj.pk)

                                if recheck_obj.count()>0:
                                    if renew_staff_check_level<3:
                                        renew_staff_check_level=3

                #エラーが3以下になるようなら更新
                obj.staff_check_level=renew_staff_check_level
                obj.save()
        """
                        

        #チェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level = staff_check_level

        form.save()
        return super(ScheduleEditView,self).form_valid(form)

    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})

class ScheduleDeleteView(StaffUserRequiredMixin,DeleteView):
    model = Schedule
    template_name ="schedules\schedule_delete.html"

    """ 
    複数のレコードがズレた時間帯で重複している可能性があり、一律でのchecklevelの解除は困難なため処理保留
    #重複していたレコードがあれば、check_levelを更新する。
    def delete(self, request, *args, **kwargs):

        endtime = self.object.start_date + datetime.timedelta(minutes = self.object.service.time)
        endtime = localtime(endtime)
        self.object.end_date = endtime

        #利用者スケジュールの重複をチェックし更新
        Schedule.objects.filter(\
            Q(careuser=self.object.careuser),Q(careuser_check_level==3),\
            (Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | \
            Q(start_date__lt=endtime,end_date__gte=endtime))).exclude(id = self.object.pk)\
            .update(careuser_check_level=0)


        #スタッフスケジュールの重複をチェックしcheck_flgを付与
        staff_obj=(self.object.staff1,self.object.staff2,self.object.staff3,self.object.staff4)


        for index,staff in enumerate(staff_obj):
            if(index < self.object.peoples):
                if(staff is not None):
                    staff_duplicate_check_obj = Schedule.objects.all().filter((Q(start_date__lte=self.object.start_date,end_date__gt=self.object.start_date) | Q(start_date__lt=endtime,end_date__gte=endtime)),\
                                                (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff))).exclude(id = self.object.pk)
                    if(len(staff_duplicate_check_obj)==1):
                           staff_duplicate_check_obj.update(staff_check_level=0)
        
        return super().delete(request, *args, **kwargs)
    """
    def get_success_url(self):
        year = self.object.start_date.year
        month = self.object.start_date.month
        return reverse_lazy('schedules:monthlylist',kwargs={'year':year ,'month':month})