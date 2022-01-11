from .models import Schedule,Report,ShowUserEnddate
from staffs.models import User
from careusers.models import CareUser
from django.db.models import Q
from django.http import HttpResponseRedirect,Http404
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin
from django.urls import reverse_lazy,reverse
from .forms import ScheduleForm,ReportForm
from django.views.generic import CreateView,ListView,UpdateView,DeleteView,View,DetailView
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode


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
        context['time_tomorrow'] = tomorrow

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

        #スタッフの誕生日判定
        staff_birthday = False
        if self.get_selected_user_obj().birthday:
            if self.get_selected_user_obj().birthday.month == now.month and self.get_selected_user_obj().birthday.day == now.day:
                staff_birthday=True

        context['staff_birthday'] = staff_birthday

        return context


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

    def get_queryset(self, **kwargs):
    
        condition_date  = self.get_condition_date()
        condition_staff = self.get_condition_staff()
        condition_show  = self.get_condition_show()

        queryset = Schedule.objects.select_related('careuser','report').all().filter(condition_date,condition_staff,condition_show).order_by('start_date')
    
        return queryset

    def get_condition_date(self, **kwargs):
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

        return condition_date

    def get_condition_staff(self):
        #管理権限のあるユーザーは選択制、ないユーザーには自己のスケジュールのみ表示
        selected_user_obj = self.get_selected_user_obj()
        
        condition_staff = search_staff_tr_query(selected_user_obj)

        return condition_staff

    def get_condition_show(self):

        #登録ヘルパーへの表示最終日時
        if ShowUserEnddate.objects.all().count()>0:
            show_enddate = ShowUserEnddate.objects.first().end_date
        else:
            show_enddate = datetime.datetime(1970,1,1)
            show_enddate = make_aware(show_enddate)

        if self.request.user.is_staff:
            condition_show  = Q()
        else:
            condition_show  = Q(start_date__lte =show_enddate)

        return condition_show


class ScheduleCalendarListView(MonthWithScheduleMixin,ListView):
    model = Schedule
    template_name = "schedules/schedule_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_data()
        context.update(calendar_context)

        #スタッフの絞込み検索用リスト
        if self.request.user.is_staff:
            #スタッフの絞込み検索用リスト
            staff_obj = User.objects.all().filter(is_active=True,kaigo=True).order_by('-is_staff','pk')
            context['staff_obj'] = staff_obj

            selected_staff = self.request.GET.get('staff')
            
            if selected_staff is not None:
                context['selected_staff'] = User.objects.get(pk=int(selected_staff))
            else:
                context['selected_staff'] = None

            #利用者の絞込み検索用リスト
            careuser_obj = CareUser.objects.all().filter(is_active=True).order_by('last_kana','first_kana')
            context['careuser_obj'] = careuser_obj

            selected_careuser = self.request.GET.get('careuser')
            
            if selected_staff is not None:
                context['selected_staff'] = User.objects.get(pk=int(selected_staff))
            elif selected_careuser is not None:
                context['selected_careuser'] = CareUser.objects.get(pk=int(selected_careuser))
            else:
                context['selected_careuser'] = None
        else:
            #スタッフの絞込み検索用リスト
            context['selected_staff'] = self.request.user

        return context

class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        #登録ヘルパーさんは自身が入っているスケジュール以外でロックされていないデータ以外表示しないようにする。
        if self.request.user.is_staff:
            #schedule_data = Report.objects.select_related('schedule').get(pk=int(pk))
            schedule_data = get_object_or_404(Report.objects.select_related('schedule'),pk=int(pk))
        else:
            schedule_data = get_object_or_404(Report.objects.select_related('schedule'),(Q(schedule__staff1=self.request.user)|Q(schedule__staff2=self.request.user)|Q(schedule__staff3=self.request.user)|Q(schedule__staff4=self.request.user)),locked=False,pk=int(pk))

        if schedule_data.locked is False and schedule_data.service_in_date is None:
            form = ReportForm(initial={
                #下記以外の項目はリセットされる
                'service_in_date' : schedule_data.schedule.start_date,
                'service_out_date': schedule_data.schedule.end_date,
                'locked':True,
            })
            context['disp_lock'] = False
            context['form'] = form
        else:
            context['disp_lock'] = True

        context['schedule_data'] = schedule_data
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #最終更新者を追記

        self.object.created_by = self.request.user
        #reportをロックする
        #初回の入力かチェック
        first_flg=False
        report_now_data = Report.objects.get(pk=int(self.object.pk))
        if report_now_data.service_in_date is None:
            first_flg=True

        #登録スタッフの場合
        if self.request.user.is_staff and first_flg is False and self.object.locked is False:
            self.object.locked=False
        #社員の場合
        else:
            self.object.locked=True
        
        form.save()
        return super(ReportUpdateView,self).form_valid(form)

    def get_success_url(self):
        year  = self.object.service_in_date.year
        month = self.object.service_in_date.month
        day   = self.object.service_in_date.day
        return reverse_lazy('schedules:dailylist',kwargs={'year':year,'month':month,'day':day})

class ReportDetailView(DetailView):
    model = Report
    template_name = "schedules/report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        #登録ヘルパーさんは自身が入っているスケジュール以外でロックされていないデータ以外表示しないようにする。
        if self.request.user.is_staff:
            #schedule_data = Report.objects.select_related('schedule').get(pk=int(pk))
            schedule_data = get_object_or_404(Report.objects.select_related('schedule'),pk=int(pk))
        else:
            #ロックされているデータは除外
            schedule_data = get_object_or_404(Report.objects.select_related('schedule'),(Q(schedule__staff1=self.request.user)|Q(schedule__staff2=self.request.user)|Q(schedule__staff3=self.request.user)|Q(schedule__staff4=self.request.user)),locked=True,pk=int(pk))

        context['schedule_data'] = schedule_data
        context['otsuri'] = schedule_data.deposit - schedule_data.payment
        
        return context


#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）

class ScheduleListView(StaffUserRequiredMixin,ListView):
    model = Schedule
    queryset = Schedule.objects.all().order_by('start_date')

    def get_day_of_week_jp(self,datetime):
        w_list = ['(月)', '(火)', '(水)', '(木)', '(金)', '(土)', '(日)']
        return(w_list[datetime.weekday()])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            context['day_start']= "today"
        elif self.kwargs.get('day'):
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
            dateday=datetime.datetime(year,month,self.kwargs.get('day'),0,0,0)
            #アンカー用にcontextで曜日付きの文字列を追加
            context['anchor_day']= str(dateday.day) + "日" + self.get_day_of_week_jp(dateday)
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
        careuser_obj = CareUser.objects.all().filter(is_active=True).order_by('last_kana','first_kana')
        context['careuser_obj'] = careuser_obj
        
        selected_careuser = self.request.GET.get('careuser')
        context['selected_careuser'] = ""
        if selected_careuser is not None:
            context['selected_careuser'] = CareUser.objects.get(pk=int(selected_careuser))

        #スタッフの絞込み検索用リスト
        staff_obj = User.objects.all().filter(is_active=True,kaigo=True).order_by('-is_staff','pk')
        context['staff_obj'] = staff_obj
        context['selected_staff'] = self.get_selected_user_obj()


        #登録ヘルパーへの表示最終日時
        if ShowUserEnddate.objects.all().count()>0:
            show_enddate = ShowUserEnddate.objects.first().end_date
        else:
            show_enddate = datetime.datetime(1970,1,1)
            show_enddate = make_aware(show_enddate)

        #表示付きの月末日時
        posted_month_last_time =datetime.datetime(year,month,1) + relativedelta(months=1) - datetime.timedelta(seconds=1)
        posted_month_last_time = make_aware(posted_month_last_time)
        if show_enddate < posted_month_last_time:
            context['showstaff_btn'] = True
        else:
            context['showstaff_btn'] = False
        
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
            condition_staff = search_staff_tr_query(User(pk=search_staff))

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

        #予定キャンセルにチェックがある場合はスタッフを空にする。
        if self.object.cancel_flg:
            self.object.staff1 = None
            self.object.staff2 = None
            self.object.staff3 = None
            self.object.staff4 = None
            self.object.tr_staff1 = None
            self.object.tr_staff2 = None
            self.object.tr_staff3 = None
            self.object.tr_staff4 = None
            
        #予定キャンセルの場合、先に上記によりスタッフをクリアしていることが必須
        #利用者スケジュールの重複をチェックしcheck_flgを付与
        careuser_check_level = 0
        staff_check_level    = 0

        if self.object.cancel_flg is False:
            #利用者データの重複チェック//////////////////////////////////////////////////////////////////////////////////////////////
            #登録するレコードと重複する、同じ時間帯・同一利用者・キャンセルでないレコードを抽出
            careuser_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(self.object.start_date,self.object.end_date),careuser=self.object.careuser,cancel_flg=False).exclude(id = self.object.pk)
            #レコードが存在すれば、新規登録するレコードと既存レコードの全てにcareuser_check_levelを3を設定
            if careuser_duplicate_check_obj.count():
                if careuser_check_level<3:
                    careuser_check_level = 3
                    #時間が重複しているレコードのcareuser_check_levelを更新する
                    careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)

            #スタッフスケジュールの重複をチェック////////////////////////////////////////////////////////////////////////////////////
            #新規スケジュールに登録されているスタッフを全員チェック
            staff_obj=staff_all_set_list(self.object)
            
            for index,staff in enumerate(staff_obj):

                if(staff is None):
                    if(index < self.object.peoples):
                        if staff_check_level < 2:
                            staff_check_level = 2
                else:
                    #同一スタッフによる、同一時間帯でキャンセルでないレコードを抽出
                    staff_duplicate_check_obj = Schedule.objects.all().filter(search_sametime_query(self.object.start_date,self.object.end_date),search_staff_tr_query(staff),cancel_flg=False).exclude(id = self.object.pk)
                    if staff_duplicate_check_obj.count():
                        if staff_check_level < 3:
                            staff_check_level = 3
                            #時間が重複しているレコードのstaff_check_levelをまとめて更新する
                            staff_duplicate_check_obj.update(staff_check_level=staff_check_level)

        #新規スケジュールにチェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level    = staff_check_level

        schedule = form.save()

        #実績記録reportレコードを作成
        Report.objects.create(schedule=schedule,created_by=self.request.user)

        return super(ScheduleCreateView,self).form_valid(form)

    def get_success_url(self):
        #return reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})
        year  = localtime(self.object.start_date).year
        month = localtime(self.object.start_date).month

        redirect_url = reverse('schedules:monthlylist',kwargs={'year':year ,'month':month})
        parameters = urlencode(dict(careuser=self.object.careuser.pk))
        url = f'{redirect_url}?{parameters}'
        return url

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

        #予定キャンセルにチェックがある場合はスタッフを空にする。
        if self.object.cancel_flg:
            self.object.staff1 = None
            self.object.staff2 = None
            self.object.staff3 = None
            self.object.staff4 = None
            self.object.tr_staff1 = None
            self.object.tr_staff2 = None
            self.object.tr_staff3 = None
            self.object.tr_staff4 = None

        #予定キャンセルの場合、先に上記によりスタッフをクリアしていることが必須
        careuser_check_level= self.sche_update_careusers(self.object)
        staff_check_level   = self.sche_update_staffs(self.object)

        #チェック結果を反映
        self.object.careuser_check_level = careuser_check_level
        self.object.staff_check_level = staff_check_level

        #時間が変更となる場合は、報告書の時間を書き換える
        #現在の予定時刻と報告書の時刻を取得
        old_data_obj = Schedule.objects.select_related('report').get(id=self.object.pk)
        st = localtime(old_data_obj.start_date)
        ed = localtime(old_data_obj.end_date)

        report_obj = Report.objects.get(schedule=old_data_obj)
        locked = report_obj.locked

        #予定時刻が変更された場合
        if st != self.object.start_date or ed != self.object.end_date:
            now  = datetime.datetime.now()
            now  = make_aware(now)

            #現在より未来に移動の場合
            if self.object.start_date > now:
                #reportの日時を空にする
                new_service_in_date  =None
                new_service_out_date =None
                #ロックを解除
                locked = False
            #現在より過去に移動の場合
            else:
                #予定時刻に修正する
                new_service_in_date  = self.object.start_date
                new_service_out_date = self.object.end_date
 
            #reportの時刻を修正
            report_obj = Report.objects.get(schedule=old_data_obj)
            report_obj.service_in_date = new_service_in_date
            report_obj.service_out_date = new_service_out_date
            report_obj.locked =  locked
            report_obj.save()

        form.save()
        return super(ScheduleEditView,self).form_valid(form)

    #利用者の時間重複しているレコードの更新
    def sche_update_careusers(self,edit_obj):

         #先に修正される前のデータと利用者と時間が重複しcheck_levelが3となっているデータを取り出し、新情報と比較してcheck_levelを更新する。////////////////////////////////////////////
        #編集前の時間情報を取得
        old_obj = Schedule.objects.get(id=edit_obj.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date

        #編集前のデータと同一利用者・同時間帯でcheck_levelが3のレコードを抽出し、check_levelを更新する。
        error_obj= Schedule.objects.all().filter(search_sametime_query(old_start_date,old_end_date),careuser=edit_obj.careuser,careuser_check_level__gte=3,cancel_flg=False).exclude(id=edit_obj.pk)

        for obj in error_obj:
            clear_flg=True
            #編集後のデータにより改善されたかチェック
            if  booking_sametime_compare(obj,edit_obj.start_date,edit_obj.end_date,edit_obj.cancel_flg):
                clear_flg=False
            else:
                #他に重複するレコードがないかチェック
                recheck_obj = Schedule.objects.all().filter(search_sametime_query(obj.start_date,obj.end_date),careuser=edit_obj.careuser,cancel_flg=False).exclude(id=edit_obj.pk).exclude(id = obj.pk)
                #重複されているレコードがある場合は改善されていない
                if recheck_obj.count():
                    clear_flg=False 
                       
            if clear_flg:
                #各レコード毎にエラー値を更新
                obj.careuser_check_level=0
                obj.save()

        #編集後のデータとの利用者スケジュールの重複をチェックしcheck_flgを付与////////////////////////////////////////////////////////////
        careuser_check_level = 0
        #編集後のレコードが予定キャンセルとなっている場合は、既に上記で変更前にエラーが出ているレコードについてすべて更新済みのため、他のレコードに新たにエラーが発生することはない
        if self.object.cancel_flg is False:
            #編集後データと同一利用者・時間帯で有効（キャンセルでない）データを抽出
            careuser_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(edit_obj.start_date,edit_obj.end_date),careuser=edit_obj.careuser,cancel_flg=False).exclude(id=edit_obj.pk)
            if careuser_duplicate_check_obj.count():
                #変更レコードのオブジェクトに返す
                careuser_check_level = 3
                #時間が重複しているレコードのcareuser_check_levelをまとめて更新する
                careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)
        
        return careuser_check_level

    #スタッフの時間重複しているレコードの更新
    def sche_update_staffs(self,edit_obj):

        #追加後・変更後オブジェクトと同一スタッフ、時間が重複していないかチェックし、重複があれば重複レコードのフラグを変更し、staff_check_levelを返す
        new_staffs = staff_all_set_list(edit_obj)
        
        #編集前のデータと重複していたレコードが、重複解消していればフラグを更新する。
        #変更前のデータを取得
        old_obj = Schedule.objects.get(id=edit_obj.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date
        old_check_staffs = staff_all_set_list(old_obj)
        
        for index,staff in enumerate(old_check_staffs):
            if staff is not None:
                #編集前のスタッフにより、エラーが出ていたキャンセルでないレコードを取得
                old_err_obj = Schedule.objects.all().filter(search_sametime_query(old_start_date,old_end_date),search_staff_tr_query(staff),staff_check_level__gte=3,cancel_flg=False).exclude(id=edit_obj.pk)
                if old_err_obj.count():
                    for obj in old_err_obj:
                        #今回の更新で重複が解消されていればフラグを更新する。
                        clear_flg=True
                        no_staff_check = False;

                        #そもそもエラーレコードの必要人数が足りているかチェック
                        for index,staff in enumerate(staff_all_set_list(obj)):
                            if(staff is None):
                                if(index < obj.peoples):
                                    staff_check_level = 2

                        #まず編集後のスタッフ・時間情報と重複していないかチェック
                        for index,stf in enumerate(new_staffs):
                            #変更後のスタッフ・時間にて比較し、エラーが改善されているかチェック
                            if stf is not None:
                                if booking_sametime_compare(obj,edit_obj.start_date,edit_obj.end_date,edit_obj.cancel_flg) and booking_samestaff_compare(obj,stf):
                                    #改善されていない場合はループを終了
                                    clear_flg=False
                                    break

                        #次にエラーのあったレコードが他に重複するレコードがないかチェック
                        recheck_staffs = staff_all_set_list(obj)
                        for stf in recheck_staffs:
                            if stf is not None:
                                recheck_obj = Schedule.objects.all().filter(search_sametime_query(obj.start_date,obj.end_date),search_staff_tr_query(stf),cancel_flg=False).exclude(id=edit_obj.pk).exclude(id = obj.pk)
                                #重複されているレコードがある場合は改善されていない
                                if recheck_obj.count():
                                    clear_flg=False

                        #改善されている場合は更新
                        if clear_flg:
                            #必要人数が足りていなければ2を、されていれば0をセット
                            if no_staff_check:
                                new_flg=2
                            else:
                                new_flg=0
                            obj.staff_check_level = new_flg
                            obj.save()


        #編集後のデータとスタッフスケジュールの重複をチェックしcheck_flgを付与////////////////////////////////////////////////////////////
        staff_check_level =0;

        for index,staff in enumerate(new_staffs):
    
            #必要人数以下の状態であれば、staff_check_levelに２を付与
            if(index < edit_obj.peoples and edit_obj.cancel_flg is False):
                if staff is None:
                    staff_check_level = 2

            if staff is not None:
                #編集後レコードのスタッフ毎に同一スタッフ、同一時間帯でキャンセルでないレコードを抽出し重複をチェック
                err_obj = Schedule.objects.all().filter(search_sametime_query(edit_obj.start_date,edit_obj.end_date),search_staff_tr_query(staff),cancel_flg=False).exclude(id=edit_obj.pk)
                #もし重複するレコードがあれば、他のレコードに重複フラグを付与
                if err_obj.count():
                    #変更レコードのオブジェクトに返す
                    staff_check_level =3;
                    #他の重複しているレコードにフラグをまとめて付与
                    err_obj.update(staff_check_level=staff_check_level)
    
        return staff_check_level

    def get_success_url(self):
        year  = localtime(self.object.start_date).year
        month = localtime(self.object.start_date).month
        #return reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})
        
        redirect_url = reverse('schedules:monthlylist',kwargs={'year':year ,'month':month})
        parameters = urlencode(dict(careuser=self.object.careuser.pk))
        url = f'{redirect_url}?{parameters}'
        return url

class ScheduleDeleteView(StaffUserRequiredMixin,DeleteView):

    model = Schedule
    template_name ="schedules/schedule_delete.html"

    def delete(self, request, *args, **kwargs):

        del_obj = self.get_object()

        #同一careuserの重複チェック
        #更新前のデータと同時間帯でエラーが出ているレコードを取得し、改善されたかどうかチェック
        error_obj= Schedule.objects.all().filter(search_sametime_query(del_obj.start_date,del_obj.end_date),careuser=del_obj.careuser,careuser_check_level=3,cancel_flg=False).exclude(id=del_obj.pk)
  
        for obj in error_obj:
            #エラーレコードが、削除データ以外に他に重複するレコードがあるかチェック
            sametime_check = Schedule.objects.all().filter(search_sametime_query(obj.start_date,obj.end_date),careuser=obj.careuser,cancel_flg=False).exclude(Q(pk=del_obj.pk) | Q(pk=obj.pk))
            if sametime_check.count():
                careuser_check_level = 3
            else:
                careuser_check_level = 0

            #エラー値を更新
            obj.careuser_check_level=careuser_check_level
            obj.save()

        #同一staffの重複チェック
        #削除前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.all().filter(search_sametime_query(del_obj.start_date,del_obj.end_date),staff_check_level=3).exclude(id = del_obj.pk)

        #今回の削除で解消される場合はエラーを削除する
        for obj in error_obj:
            renew_staff_check_level=0;
            check_staffs_obj = staff_all_set_list(obj)
            #削除されるレコードとエラーレコードを比較
            for index,stf in enumerate(check_staffs_obj):
                #エラーレコードのスタッフ選択状況
                if(stf is None):
                    if(index < obj.peoples):
                        if(renew_staff_check_level<2):
                            renew_staff_check_level = 2
                else:
                    #エラーレコードが削除レコード以外のレコードと時間、スタッフが重複していないかチェック
                    recheck_obj= Schedule.objects.all().filter(search_sametime_query(obj.start_date,obj.end_date),search_staff_tr_query(stf)).exclude(id=del_obj.pk).exclude(id=obj.pk)
                    if recheck_obj.count():
                        if renew_staff_check_level<3:
                            renew_staff_check_level=3

            #エラー値を更新
            obj.staff_check_level=renew_staff_check_level
            obj.save()
        if del_obj.def_sche is not None:
            raise Http404
        else:    
            return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        year  = localtime(self.object.start_date).year
        month = localtime(self.object.start_date).month
        day   = localtime(self.object.start_date).day
        return reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})


class ScheduleShowStaffView(SuperUserRequiredMixin,View):

    def get(self,request, **kwargs):
        #model = Schedule
        year = self.kwargs.get('year')
        month= self.kwargs.get('month')

        show_enddate = datetime.datetime(year,month,1) + relativedelta(months=1) - datetime.timedelta(seconds=1)
        show_enddate = make_aware(show_enddate)

        #更新
        ShowUserEnddate.objects.update_or_create(end_date=show_enddate,updated_by=self.request.user)

        return HttpResponseRedirect(reverse('schedules:monthlylist', kwargs=dict(year=year,month=month)))

def search_staff_tr_query(staff):
    cond = (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)|Q(tr_staff1=staff)|Q(tr_staff2=staff)|Q(tr_staff3=staff)|Q(tr_staff4=staff))
    return cond

def search_sametime_query(start,end):

     #全く同じ時間の場合
    cond1 = Q(start_date=start,end_date=end)
    #一部が重なる場合
    cond2 = Q(start_date__gte=start,start_date__lt=end) | Q(end_date__gt=start,end_date__lte=end)
     #内包する場合
    cond3 = Q(start_date__lte=start,end_date__gte=end) | Q(start_date__gte=start,end_date__lte=end)

    cond = (cond1 | cond2 | cond3)
    return cond

def booking_sametime_compare(check_obj,date_start,date_end,date_cancel_flg):

    #どちらかがキャンセルの場合
    if check_obj.cancel_flg==True or date_cancel_flg == True:
        return False
    #全く同じ時間の場合
    elif check_obj.start_date==date_start and check_obj.end_date == date_end:
        return True
    #一部が重なる場合
    elif check_obj.start_date < date_start and check_obj.end_date > date_start and check_obj.end_date <= date_end:
        return True
    elif check_obj.start_date >= date_start and check_obj.start_date < date_end and check_obj.end_date > date_end:
        return True
    #内包する場合
    elif check_obj.start_date < date_start and check_obj.end_date > date_end:
        return True
    elif check_obj.start_date > date_start and check_obj.end_date < date_end:
        return True
    else:
        return False

def booking_samestaff_compare(check_obj,staff):
    if check_obj.staff1 == staff:
        return True
    elif check_obj.staff2 == staff:
        return True
    elif check_obj.staff2 == staff:
        return True
    elif check_obj.staff2 == staff:
        return True
    elif check_obj.tr_staff1 == staff:
        return True
    elif check_obj.tr_staff2 == staff:
        return True
    elif check_obj.tr_staff2 == staff:
        return True
    elif check_obj.tr_staff2 == staff:
        return True
    else:
        return False

def staff_all_set_list(obj):
    rt_list = []
    rt_list.append(obj.staff1)
    rt_list.append(obj.staff2)
    rt_list.append(obj.staff3)
    rt_list.append(obj.staff4)
    rt_list.append(obj.tr_staff1)
    rt_list.append(obj.tr_staff2)
    rt_list.append(obj.tr_staff3)
    rt_list.append(obj.tr_staff4)
    
    return rt_list
    