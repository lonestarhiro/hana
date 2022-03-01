from .models import Schedule,Report,ShowUserEnddate,AddRequest
from staffs.models import User
from careusers.models import CareUser,Service
from django.db.models import Q,Max,Prefetch
from django.conf import settings
from django.http import HttpResponseRedirect,Http404
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,MonthWithScheduleMixin
from django.urls import reverse_lazy,reverse
from .forms import ScheduleForm,ReportForm,AddRequestForm
from django.views.generic import CreateView,ListView,UpdateView,DeleteView,TemplateView,View,DetailView
import datetime
import math
import requests
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from django.core.mail import send_mail


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

        #画面推移後の戻るボタン用にpathをセッションに記録
        self.request.session['from'] = self.request.get_full_path()

        #スタッフの絞込み検索用リスト
        if self.request.user.is_staff:
            staff_obj = User.objects.filter(is_active=True,kaigo=True).order_by('-is_staff','last_kana','first_kana')
            context['staff_obj'] = furigana_index_list(staff_obj,"staffs")

        #選択中のユーザー
        context['selected_staff'] = self.get_selected_user_obj()

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

        queryset = Schedule.objects.select_related('careuser','report').filter(condition_date,condition_staff,condition_show,cancel_flg=False).order_by('start_date')
    
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
        if ShowUserEnddate.objects.all():
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
            staff_obj = User.objects.filter(is_active=True,kaigo=True).order_by('-is_staff','last_kana','first_kana')
            context['staff_obj'] = furigana_index_list(staff_obj,"staffs")

            selected_staff = self.request.GET.get('staff')
            
            if selected_staff:
                context['selected_staff'] = User.objects.get(pk=int(selected_staff))
            else:
                context['selected_staff'] = None

            #利用者の絞込み検索用リスト
            careuser_obj = CareUser.objects.filter(is_active=True).order_by('last_kana','first_kana')
            context['careuser_obj'] = furigana_index_list(careuser_obj,"careusers")

            selected_careuser = self.request.GET.get('careuser')
            
            if selected_staff:
                context['selected_staff'] = User.objects.get(pk=int(selected_staff))
            elif selected_careuser:
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

    def get_object(self, **kwargs):
        pk = self.kwargs.get('pk')
        #登録ヘルパーは自身が入っているスケジュール以外でロックされていないデータ以外表示しないようにする。
        if self.request.user.is_staff:
            #obj = Report.objects.select_related('schedule').get(pk=int(pk))
            obj = get_object_or_404(Report.objects.prefetch_related(Prefetch("schedule",queryset=Schedule.objects.select_related('service'),to_attr="sche")),pk=int(pk))
            #print(list(vars(obj.sche.service)))
        else:
            obj = get_object_or_404(Report.objects.prefetch_related(Prefetch("schedule",queryset=Schedule.objects.select_related('service'),to_attr="sche")),search_relate_staff_tr_query(self.request.user),careuser_confirmed=False,pk=int(pk))
        return obj

    def get_initial(self):
        initial = super().get_initial()
        initial={}
        if not self.object.service_in_date  : initial['service_in_date']  = self.object.schedule.start_date
        if not self.object.service_out_date : initial['service_out_date'] = self.object.schedule.end_date
        if not self.object.in_time_main     : initial['in_time_main']     = self.object.schedule.service.in_time_main
        if not self.object.in_time_sub      : initial['in_time_sub']      = self.object.schedule.service.in_time_sub
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helpers=""
        if self.object.schedule.peoples == 1:
            helpers += str(self.object.schedule.staff1)
        elif self.object.schedule.peoples == 2:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2)
        elif self.object.schedule.peoples == 3:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff3)
        elif self.object.schedule.peoples == 4:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff3) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff4)
        if self.object.schedule.tr_staff1:
            helpers += " <br class=\"d-md-none\">[同行] " + str(self.object.schedule.tr_staff1)
        if self.object.schedule.tr_staff2:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff2)
        if self.object.schedule.tr_staff3:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff3)
        if self.object.schedule.tr_staff4:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff4)
        context['helpers'] = helpers
        
        return context

    def form_valid(self, form):
        valid_form = form.save(commit=False)

        #最終更新者を追記
        valid_form.created_by = self.request.user

        if valid_form.deposit is None:
            valid_form.deposit = 0;
        
        if valid_form.payment is None:
            valid_form.payment = 0;
        
        valid_form.error_code = repo_check_errors(valid_form,self.object.schedule)
        valid_form.warnings   = repo_check_warnings(valid_form,self.object.schedule)
        valid_form.error_warn_allowed = False

        form.save()
        return super(ReportUpdateView,self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('schedules:report_detail',kwargs={'pk':self.object.pk})

class ReportDetailView(DetailView):
    model = Report
    template_name = "schedules/report_detail.html"

    def get_object(self, **kwargs):
        pk = self.kwargs.get('pk')
        #登録ヘルパーさんは自身が入っているスケジュール以外は表示しないようにする。
        if self.request.user.is_staff:
            #obj = Report.objects.select_related('schedule').get(pk=int(pk))
            obj = get_object_or_404(Report.objects.prefetch_related(Prefetch("schedule",queryset=Schedule.objects.select_related('careuser'),to_attr="sche")),pk=int(pk))
        else:
            #登録ヘルパーさん用
            obj = get_object_or_404(Report.objects.prefetch_related(Prefetch("schedule",queryset=Schedule.objects.select_related('careuser'),to_attr="sche")),search_relate_staff_tr_query(self.request.user),pk=int(pk))
        #未入力のデータは404を出力して終了
        if obj.service_in_date is None or obj.service_out_date is None:
            raise Http404("lookup error")

        #利用者確認ボタンが押されたら、ロックを掛ける
        if obj.careuser_confirmed is False and self.request.GET.get('careuser_confirmed'):

            #送信登録がされている場合は送信
            #未送信の場合、または再送信チェックが押されている場合に限る
            if obj.schedule.careuser.report_send and obj.schedule.careuser.report_email and (not obj.email_sent_date or (self.request.user.is_staff and self.request.GET.get('resend_check'))) :
                
                #メール送信用テキストを作成
                subject = "介護ステーションはな　サービス実施報告"
                message = make_email_message(obj)
                from_email = settings.DEFAULT_FROM_EMAIL  # 送信者
                recipient_list = ["obj.schedule.careuser.report_email"]  # 宛先リスト
                send_mail(subject, message, from_email, recipient_list)
                
                #送信日時を記録
                obj.email_sent_date = make_aware(datetime.datetime.now())

            obj.careuser_confirmed = True
            obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['repo'] = report_for_output(self.object)
        
        helpers=""
        if self.object.schedule.peoples == 1:
            helpers += str(self.object.schedule.staff1)
        elif self.object.schedule.peoples == 2:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2)
        elif self.object.schedule.peoples == 3:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff3)
        elif self.object.schedule.peoples == 4:
            helpers += str(self.object.schedule.staff1) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff2) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff3) + "<br class=\"d-md-none\">" + str(self.object.schedule.staff4)
        if self.object.schedule.tr_staff1:
            helpers += " <br class=\"d-md-none\">[同行] " + str(self.object.schedule.tr_staff1)
        if self.object.schedule.tr_staff2:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff2)
        if self.object.schedule.tr_staff3:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff3)
        if self.object.schedule.tr_staff4:
            helpers += "<br class=\"d-md-none\">" + str(self.object.schedule.tr_staff4)
        context['helpers'] = helpers
        
        return context

class AddRequestView(CreateView):
    model = AddRequest
    form_class = AddRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get('done'):
            context['done'] = self.request.GET.get('done')

        return context

    def get_initial(self):
        now = datetime.datetime.now()
        now = make_aware(now)
        set_date = datetime.datetime(now.year,now.month,now.day,now.hour) + datetime.timedelta(hours=1)

        initial = super().get_initial()
        initial={}
        initial['start_date']  = set_date

        return initial    
    
    def form_valid(self, form):
        formobj = form.save(commit=False)
        #最終更新者を追記
        formobj.created_by = self.request.user
        disp_care_user = formobj.careuser_txt.replace('　', ' ').strip(' ')
        form.save()
        msg= str(self.request.user) + "様より" + disp_care_user + "様分のスケジュール追加依頼が届きました。はなオンラインの「各種管理」をご確認の上、追加をお願いします。"
        line_send(msg)

        return super(AddRequestView,self).form_valid(form)

    def get_success_url(self):
        redirect_url = reverse_lazy('schedules:add_request')
        parameters = urlencode(dict(done="success"))
        ret = f'{redirect_url}?{parameters}'

        return ret


#以下staffuserのみ表示（下のStaffUserRequiredMixinにて制限中）/////////////////////////////////////////////////////////////////////////////////////

class ScheduleListView(StaffUserRequiredMixin,ListView):
    model = Schedule

    def get_day_of_week_jp(self,datetime):
        w_list = ['(月)', '(火)', '(水)', '(木)', '(金)', '(土)', '(日)']
        return(w_list[datetime.weekday()])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
            day   = datetime.datetime.today().day
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
        
            if self.kwargs.get('day'):
                day = self.kwargs.get('day')
            else:
                day=None

        if day:
            dateday=datetime.datetime(year,month,day,0,0,0)
            #アンカー用にcontextで曜日付きの文字列を追加
            context['anchor_day']= str(dateday.day) + "日" + self.get_day_of_week_jp(dateday)
            context['posted_day']= self.kwargs.get('day')
        
        this_month   = datetime.datetime(year,month,1)
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)
        context['this_month']   = this_month
        context['next_month']   = next_month
        context['before_month'] = before_month

        now = datetime.datetime.now()
        now = make_aware(now)
        context['time_now'] = now

        #画面推移後の戻るボタン用にpathをセッションに記録
        self.request.session['from'] = self.request.get_full_path()

        #利用者の絞込み検索用リスト
        #過去の履歴を確認できるようスーパーユーザーのみ全表示にする。
        if self.request.user.is_superuser:
            careuser_obj = CareUser.objects.order_by('last_kana','first_kana')
        else:    
            careuser_obj = CareUser.objects.filter(is_active=True).order_by('last_kana','first_kana')
        context['careuser_obj'] = furigana_index_list(careuser_obj,"careusers")
        
        selected_careuser = self.request.GET.get('careuser')
        context['selected_careuser'] = ""
        if selected_careuser:
            context['selected_careuser'] = CareUser.objects.get(pk=int(selected_careuser))

        #スタッフの絞込み検索用リスト
        #過去の履歴を確認できるよう事務権限のみ全表示にする。
        if self.request.user.jimu:
            staff_obj = User.objects.filter(kaigo=True).order_by('-is_staff','last_kana','first_kana')
        else:
            staff_obj = User.objects.filter(is_active=True,kaigo=True).order_by('-is_staff','last_kana','first_kana')
        context['staff_obj'] = furigana_index_list(staff_obj,"staffs")
        context['selected_staff'] = self.get_selected_user_obj()

        #サービス分類の絞込み検索用リスト        
        query = Service.objects.all().order_by('kind')
        kind_list={}
        for sv in query:
            if sv.kind in kind_list:
                continue
            kind_list[sv.kind] = sv.get_kind_display()
        context['service_kind_obj'] = kind_list

        service_kind = self.request.GET.get('service_kind')
        if(service_kind):
            context['selected_service_kind'] = int(service_kind)

        return context
    
    def get_queryset(self, **kwargs):
        #表示期間
        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')
        
        st= datetime.datetime(year,month,1)
        ed= st + relativedelta(months=1)
        st = make_aware(st)
        ed = make_aware(ed)
        condition_date = Q(start_date__range=[st,ed])

        #利用者絞込み
        condition_careuser = Q()
        search_careuser = self.request.GET.get('careuser',default=None)
        if search_careuser:
            condition_careuser = Q(careuser=CareUser(pk=search_careuser))

        #スタッフ絞込み
        condition_staff = Q()
        search_staff = self.get_selected_user_obj()
        if search_staff:
            #変数を上書き
            search_staff = self.get_selected_user_obj().pk
            condition_staff = search_staff_tr_query(User(pk=search_staff))

        #サービス種別絞込み
        condition_service_kind = Q()
        kind = self.request.GET.get('service_kind')
        if kind:
            #変数を上書き
            condition_service_kind = Q(service__kind=kind)

        queryset = Schedule.objects.select_related('report','careuser','service','staff1','staff2','staff3','staff4').filter(condition_date,condition_careuser,condition_staff,condition_service_kind).order_by('start_date')
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
        self.object.created_by = self.request.user

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
            if careuser_duplicate_check_obj:
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
                    staff_duplicate_check_obj = Schedule.objects.filter(search_sametime_query(self.object.start_date,self.object.end_date),search_staff_tr_query(staff),cancel_flg=False).exclude(id = self.object.pk)
                    if staff_duplicate_check_obj:
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
        if self.request.session['from']:
            ret = self.request.session['from']
        else:
            year  = localtime(self.object.start_date).year
            month = localtime(self.object.start_date).month
            redirect_url = reverse('schedules:monthlylist',kwargs={'year':year ,'month':month})
            parameters = urlencode(dict(careuser=self.object.careuser.pk))
            ret = f'{redirect_url}?{parameters}'
        return ret

class ScheduleEditView(StaffUserRequiredMixin,UpdateView):
    model = Schedule
    form_class = ScheduleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = localtime(self.object.start_date)
        context['start_date'] = start_date
        context['created_at'] = localtime(self.object.created_at)
        if self.object.created_by.last_name != "春日":
            context['created_by'] = self.object.created_by
        if self.object.updated_at:
            context['updated_at']  = localtime(self.object.updated_at)

        return context

    def form_valid(self, form):

        valid_form = form.save(commit=False)
        
        #終了日時を追記
        new_start = localtime(valid_form.start_date)
        new_end = new_start + datetime.timedelta(minutes = valid_form.service.time)
        valid_form.end_date = new_end

        #最終更新者を更新
        if self.request.user.last_name != "春日":            
            valid_form.created_by = self.request.user
            valid_form.updated_at = make_aware(datetime.datetime.now())

        #予定キャンセルにチェックがある場合はスタッフを空にする。
        if valid_form.cancel_flg:
            valid_form.staff1 = None
            valid_form.staff2 = None
            valid_form.staff3 = None
            valid_form.staff4 = None
            valid_form.tr_staff1 = None
            valid_form.tr_staff2 = None
            valid_form.tr_staff3 = None
            valid_form.tr_staff4 = None

        #予定キャンセルの場合、先に上記によりスタッフをクリアしていることが必須
        careuser_check_level= self.sche_update_careusers(valid_form)
        staff_check_level   = self.sche_update_staffs(valid_form)

        #チェック結果を反映
        valid_form.careuser_check_level = careuser_check_level
        valid_form.staff_check_level = staff_check_level

        #時間が変更となる場合は、報告書の時間を書き換える
        #現在の予定時刻と報告書の時刻を取得
        old_data_obj = Schedule.objects.select_related('report','careuser','service','staff1','staff2','staff3','staff4','tr_staff1','tr_staff2','tr_staff3','tr_staff4').get(id=valid_form.pk)
        old_start    = localtime(old_data_obj.start_date)
        old_end      = localtime(old_data_obj.end_date)

        report_obj = Report.objects.get(schedule=old_data_obj)
        careuser_confirmed = report_obj.careuser_confirmed

        now  = datetime.datetime.now()
        now  = make_aware(now)

        change_date_flg    = False
        change_service_flg = False

        #予定時刻が変更された場合
        if old_start != valid_form.start_date or old_end != valid_form.end_date  :

            #現在より未来に移動の場合
            if valid_form.start_date > now:
                #reportの日時を空にする
                new_service_in_date  =None
                new_service_out_date =None

                #利用者確認済みを解除
                careuser_confirmed = False

            #現在より過去に移動の場合
            else:
                #予定時刻を修正する
                new_service_in_date  = valid_form.start_date
                new_service_out_date = new_end

            #reportの時刻を修正
            report_obj.service_in_date    = new_service_in_date
            report_obj.service_out_date   = new_service_out_date
            report_obj.careuser_confirmed = careuser_confirmed

            change_date_flg = True

        
        #新しいサービス内容を取得
        new_serv = Service.objects.get(id=valid_form.service.id)
        #サービス内容が変更の場合
        if old_data_obj.service != valid_form.service:
            
            if new_serv.mix_items:
                #現在より未来に移動の場合
                if valid_form.start_date > now:
                    in_time_main = 0
                    in_time_sub  = 0
                    mix_reverse  = False
                #現在より過去に移動の場合
                else:
                    in_time_main = new_serv.in_time_main
                    in_time_sub  = new_serv.in_time_sub
                    mix_reverse  = new_serv=False
            else:
                in_time_main = 0
                in_time_sub  = 0
                mix_reverse  = False

            report_obj.in_time_main = in_time_main
            report_obj.in_time_sub  = in_time_sub
            report_obj.mix_reverse  = mix_reverse

            change_service_flg = True

        report_obj.error_code = repo_check_errors(report_obj,valid_form)
        report_obj.warnings   = repo_check_warnings(report_obj,valid_form)
        report_obj.error_warn_allowed = False
        report_obj.save()


        #関係スタッフにメール送信
        show_enddate = ShowUserEnddate.objects.first().end_date

        if valid_form.start_date > now and old_start < show_enddate or new_start < show_enddate:

            #送信先
            old_staff = []
            if not old_data_obj.cancel_flg:
                if old_data_obj.staff1:old_staff.append(old_data_obj.staff1)
                if old_data_obj.staff2:old_staff.append(old_data_obj.staff2)
                if old_data_obj.staff3:old_staff.append(old_data_obj.staff3)
                if old_data_obj.staff4:old_staff.append(old_data_obj.staff4)
                if old_data_obj.tr_staff1:old_staff.append(old_data_obj.tr_staff1)
                if old_data_obj.tr_staff2:old_staff.append(old_data_obj.tr_staff2)
                if old_data_obj.tr_staff3:old_staff.append(old_data_obj.tr_staff3)
                if old_data_obj.tr_staff4:old_staff.append(old_data_obj.tr_staff4)

            new_staff = []
            if not valid_form.cancel_flg:
                if valid_form.staff1:new_staff.append(valid_form.staff1)
                if valid_form.staff2:new_staff.append(valid_form.staff2)
                if valid_form.staff3:new_staff.append(valid_form.staff3)
                if valid_form.staff4:new_staff.append(valid_form.staff4)
                if valid_form.tr_staff1:new_staff.append(valid_form.tr_staff1)
                if valid_form.tr_staff2:new_staff.append(valid_form.tr_staff2)
                if valid_form.tr_staff3:new_staff.append(valid_form.tr_staff3)
                if valid_form.tr_staff4:new_staff.append(valid_form.tr_staff4)

            #全送信先リスト
            send_list =[]
            if old_staff:
                send_list.extend(old_staff)
            if new_staff:
                send_list.extend(new_staff)
            send_list = set(send_list)#重複を除去

            for send_for in send_list:

                send_flg = False

                messege = str(send_for) + "　様\n\n\n"
                messege += "平素より 介護ステーションはな の業務にご尽力賜りありがとうございます。\n"
                messege += "以下の通り、スケジュールが変更されましたのでお知らせ致します。\n\n\n"
                messege += "[利用者様] " + old_data_obj.careuser.get_short_name() + " 様\n\n"

                old_date_str = old_start.strftime("%m/%d %H:%M") + "～" + old_end.strftime("%H:%M")
                new_date_str = new_start.strftime("%m/%d %H:%M") + "～" + new_end.strftime("%H:%M")

                #新スタッフリストにない場合、またはキャンセルに変更された場合はキャンセル連絡
                if send_for in old_staff and not send_for in new_staff or not old_data_obj.cancel_flg and valid_form.cancel_flg:
                    messege += old_date_str + " " + old_data_obj.service.title
                    messege += " → キャンセル"
                    send_flg = True
                #旧スタッフリストにない場合、または旧情報がキャンセルだった場合は追加連絡
                elif not send_for in old_staff and send_for in new_staff or old_data_obj.cancel_flg and not valid_form.cancel_flg:
                    messege += "[追加]  "
                    messege += new_date_str + " " + new_serv.title
                    send_flg = True
                elif change_date_flg or change_service_flg:
                    if not change_date_flg:
                        messege += "[サービス内容変更]  " + old_date_str + " " + str(old_data_obj.service) + " → "+ str(new_serv) + "\n\n"
                        send_flg = True
                    else:
                        messege += "[変更前]  " + old_date_str + " " + old_data_obj.service.title + "\n\n"
                        messege += "[変更後]  " + new_date_str + " " + new_serv.title
                        send_flg = True

                messege += "\n\n\n以上、ご確認の程、どうぞ宜しくお願い致します。"
                messege += "\n\n"
                messege += "---------------------------------------------------------------------------------\n"
                messege += "このメールは「はなオンライン」より自動的にお送りしております。\n"
                messege += "ご返信いただいても回答いたしかねますのでご了承ください。\n"
                messege += "---------------------------------------------------------------------------------\n"

                if send_flg:
                    subject = "介護スケジュール変更のお知らせ"
                    from_email = settings.DEFAULT_FROM_EMAIL  # 送信者
                    recipient_list=[]
                    recipient_list.append(send_for.email)
                    send_mail(subject, messege, from_email, recipient_list)

        form.save()
        return super(ScheduleEditView,self).form_valid(form)

    def get_success_url(self):

        if self.request.session['from']:
            ret = self.request.session['from']
        else:
            year  = localtime(self.object.start_date).year
            month = localtime(self.object.start_date).month
            redirect_url = reverse('schedules:monthlylist',kwargs={'year':year ,'month':month})
            parameters = urlencode(dict(careuser=self.object.careuser.pk))
            ret = f'{redirect_url}?{parameters}'
        return ret

    #利用者の時間重複しているレコードの更新
    def sche_update_careusers(self,edit_obj):

         #先に修正される前のデータと利用者と時間が重複しcheck_levelが3となっているデータを取り出し、新情報と比較してcheck_levelを更新する。////////////////////////////////////////////
        #編集前の時間情報を取得
        old_obj = Schedule.objects.get(id=edit_obj.pk)
        old_start_date = old_obj.start_date
        old_end_date   = old_obj.end_date

        #編集前のデータと同一利用者・同時間帯でcheck_levelが3のレコードを抽出し、check_levelを更新する。
        error_obj= Schedule.objects.select_related('report','service').filter(search_sametime_query(old_start_date,old_end_date),careuser=edit_obj.careuser,careuser_check_level__gte=3,cancel_flg=False).exclude(id=edit_obj.pk)

        for obj in error_obj:
            clear_flg=True
            #編集後のデータにより改善されたかチェック
            if  booking_sametime_compare(obj,edit_obj.start_date,edit_obj.end_date,edit_obj.cancel_flg):
                clear_flg=False
            else:
                #他に重複するレコードがないかチェック
                recheck_obj = Schedule.objects.filter(search_sametime_query(obj.start_date,obj.end_date),careuser=edit_obj.careuser,cancel_flg=False).exclude(id=edit_obj.pk).exclude(id = obj.pk)
                #重複されているレコードがある場合は改善されていない
                if recheck_obj:
                    clear_flg=False 
                       
            if clear_flg:
                #各レコード毎にエラー値を更新
                obj.careuser_check_level=0
                obj.save()
                #レポートのエラーを更新
                if(obj.report.careuser_confirmed):
                    obj.report.error_code = repo_check_errors(obj.report,obj)
                    obj.report.warnings   = repo_check_warnings(obj.report,obj)
                    obj.report.error_warn_allowed = False
                    obj.report.save()

        #編集後のデータとの利用者スケジュールの重複をチェックしcheck_flgを付与////////////////////////////////////////////////////////////
        careuser_check_level = 0
        #編集後のレコードが予定キャンセルとなっている場合は、既に上記で変更前にエラーが出ているレコードについてすべて更新済みのため、他のレコードに新たにエラーが発生することはない
        if self.object.cancel_flg is False:
            #編集後データと同一利用者・時間帯で有効（キャンセルでない）データを抽出
            careuser_duplicate_check_obj = Schedule.objects.select_related('report','service').filter(search_sametime_query(edit_obj.start_date,edit_obj.end_date),careuser=edit_obj.careuser,cancel_flg=False).exclude(id=edit_obj.pk)
            if careuser_duplicate_check_obj:
                #変更レコードのオブジェクトに返す
                careuser_check_level = 3
                #時間が重複しているレコードのcareuser_check_levelをまとめて更新する
                careuser_duplicate_check_obj.update(careuser_check_level=careuser_check_level)

                #レポートのエラーを更新
                for obj in careuser_duplicate_check_obj:
                    if(obj.report.careuser_confirmed):
                        obj.report.error_code = repo_check_errors(obj.report,obj)
                        obj.report.warnings   = repo_check_warnings(obj.report,obj)
                        obj.report.error_warn_allowed = False
                        obj.report.save()
        
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
            if staff:
                #編集前のスタッフにより、エラーが出ていたキャンセルでないレコードを取得
                old_err_obj = Schedule.objects.select_related('report','service').filter(search_sametime_query(old_start_date,old_end_date),search_staff_tr_query(staff),staff_check_level__gte=3,cancel_flg=False).exclude(id=edit_obj.pk)
                if old_err_obj:
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
                            if stf:
                                if booking_sametime_compare(obj,edit_obj.start_date,edit_obj.end_date,edit_obj.cancel_flg) and booking_samestaff_compare(obj,stf):
                                    #改善されていない場合はループを終了
                                    clear_flg=False
                                    break

                        #次にエラーのあったレコードが他に重複するレコードがないかチェック
                        recheck_staffs = staff_all_set_list(obj)
                        for stf in recheck_staffs:
                            if stf:
                                recheck_obj = Schedule.objects.filter(search_sametime_query(obj.start_date,obj.end_date),search_staff_tr_query(stf),cancel_flg=False).exclude(id=edit_obj.pk).exclude(id = obj.pk)
                                #重複されているレコードがある場合は改善されていない
                                if recheck_obj:
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

                            #レポートのエラーを更新
                            if(obj.report.careuser_confirmed):
                                obj.report.error_code = repo_check_errors(obj.report,obj)
                                obj.report.warnings   = repo_check_warnings(obj.report,obj)
                                obj.report.error_warn_allowed = False
                                obj.report.save() 

        #編集後のデータとスタッフスケジュールの重複をチェックしcheck_flgを付与////////////////////////////////////////////////////////////
        staff_check_level =0;

        for index,staff in enumerate(new_staffs):
    
            #必要人数以下の状態であれば、staff_check_levelに２を付与
            if(index < edit_obj.peoples and edit_obj.cancel_flg is False):
                if staff is None:
                    staff_check_level = 2

            if staff:
                #編集後レコードのスタッフ毎に同一スタッフ、同一時間帯でキャンセルでないレコードを抽出し重複をチェック
                err_obj = Schedule.objects.select_related('report','service').filter(search_sametime_query(edit_obj.start_date,edit_obj.end_date),search_staff_tr_query(staff),cancel_flg=False).exclude(id=edit_obj.pk)
                #もし重複するレコードがあれば、他のレコードに重複フラグを付与
                if err_obj:
                    #変更レコードのオブジェクトに返す
                    staff_check_level =3;
                    #他の重複しているレコードにフラグをまとめて付与
                    err_obj.update(staff_check_level=staff_check_level)

                    #レポートのエラーを更新
                    for obj in err_obj:
                        if(obj.report.careuser_confirmed):
                            obj.report.error_code = repo_check_errors(obj.report,obj)
                            obj.report.warnings   = repo_check_warnings(obj.report,obj)
                            obj.report.error_warn_allowed = False
                            obj.report.save()
    
        return staff_check_level

class ScheduleDeleteView(StaffUserRequiredMixin,DeleteView):

    model = Schedule
    template_name ="schedules/schedule_delete.html"

    def delete(self, request, *args, **kwargs):

        del_obj = self.get_object()

        #同一careuserの重複チェック
        #更新前のデータと同時間帯でエラーが出ているレコードを取得し、改善されたかどうかチェック
        error_obj= Schedule.objects.select_related('report','service').filter(search_sametime_query(del_obj.start_date,del_obj.end_date),careuser=del_obj.careuser,careuser_check_level=3,cancel_flg=False).exclude(id=del_obj.pk)
  
        for obj in error_obj:
            #エラーレコードが、削除データ以外に他に重複するレコードがあるかチェック
            sametime_check = Schedule.objects.filter(search_sametime_query(obj.start_date,obj.end_date),careuser=obj.careuser,cancel_flg=False).exclude(Q(pk=del_obj.pk) | Q(pk=obj.pk))
            if sametime_check:
                careuser_check_level = 3
            else:
                careuser_check_level = 0

            #エラー値を更新
            obj.careuser_check_level=careuser_check_level
            obj.save()
            #レポートのエラーを更新
            obj.report.error_code = repo_check_errors(obj.report,obj)
            obj.report.warnings   = repo_check_warnings(obj.report,obj)
            obj.report.error_warn_allowed = False
            obj.report.save()

        #同一staffの重複チェック
        #削除前のデータと同時間帯でエラーが出ているレコードを取得
        error_obj= Schedule.objects.select_related('report','service').filter(search_sametime_query(del_obj.start_date,del_obj.end_date),staff_check_level=3).exclude(id = del_obj.pk)

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
                    recheck_obj= Schedule.objects.filter(search_sametime_query(obj.start_date,obj.end_date),search_staff_tr_query(stf)).exclude(id=del_obj.pk).exclude(id=obj.pk)
                    if recheck_obj:
                        if renew_staff_check_level<3:
                            renew_staff_check_level=3

            #エラー値を更新
            obj.staff_check_level=renew_staff_check_level
            obj.save()
            #レポートのエラーを更新
            obj.report.error_code = repo_check_errors(obj.report,obj)
            obj.report.warnings   = repo_check_warnings(obj.report,obj)
            obj.report.error_warn_allowed = False
            obj.report.save()

        if self.request.user.is_superuser is False and del_obj.def_sche:
            raise Http404
        else:    
            return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        if self.request.session['from']:
            ret = self.request.session['from']
        else:
            year  = localtime(self.object.start_date).year
            month = localtime(self.object.start_date).month
            day   = localtime(self.object.start_date).day
            ret   = reverse_lazy('schedules:dayselectlist',kwargs={'year':year ,'month':month,'day':day})
        return ret


class ScheduleShowStaffView(SuperUserRequiredMixin,View):

    def get(self,request, **kwargs):
        year = self.kwargs.get('year')
        month= self.kwargs.get('month')
        show_enddate = datetime.datetime(year,month,1) + relativedelta(months=1) - datetime.timedelta(seconds=1)
        show_enddate = make_aware(show_enddate)
        #テーブルを空にする
        ShowUserEnddate.objects.all().delete()
        #追加
        ShowUserEnddate.objects.get_or_create(end_date=show_enddate,updated_by=self.request.user)
        if self.request.session['from']:
            url = self.request.session['from']
        else:
            url = reverse('schedules:manage_top_thismonth')
        return HttpResponseRedirect(url)

class ConfirmedAddRequestView(StaffUserRequiredMixin,View):
    
    def get(self,request, **kwargs):
        pk = self.kwargs.get('pk')
        q=AddRequest.objects.get(id=int(pk))
        q.confirmed_by = self.request.user
        q.confirmed_at = make_aware(datetime.datetime.now())
        q.save()

        if self.request.session['from']:
            url = self.request.session['from']
        else:
            url = reverse('schedules:manage_top_thismonth')
        return HttpResponseRedirect(url)

class ManageTopView(StaffUserRequiredMixin,TemplateView):
    template_name = "schedules/manage_top.html"

    def get(self,request, **kwargs):
        if self.request.GET.get('warn_allow'):
            pk = int(self.request.GET.get('warn_allow'))
            q=Report.objects.get(id=pk)
            if q.error_code == 0:
                q.error_warn_allowed = True
                q.save()
        return super().get(request,**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.kwargs.get('year')==None or self.kwargs.get('month')==None:
            year  = datetime.datetime.today().year
            month = datetime.datetime.today().month
        else:
            year = self.kwargs.get('year')
            month= self.kwargs.get('month')

        this_month   = datetime.datetime(year,month,1)
        this_month   = make_aware(this_month)
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)
        next_2month  = next_month + relativedelta(months=1) 
        context['this_month']   = this_month
        context['next_month']   = next_month
        context['before_month'] = before_month

        #画面の移動関係なく、現在時刻の月初と翌月月初
        now_month = datetime.datetime(datetime.datetime.today().year,datetime.datetime.today().month,1)
        now_month = make_aware(now_month)
        now_nextmonth = now_month + relativedelta(months=1)
        context['now_month']     = now_month
        context['now_nextmonth'] = now_nextmonth

        #画面推移後の戻るボタン用にpathをセッションに記録
        self.request.session['from'] = self.request.get_full_path()

        #エラーチェック済みも再表示
        if self.request.GET.get('show_allerrors'):
            context['show_allerrors'] = True

        #スクロール値
        if self.request.GET.get('scr'):
            context['scroll'] = self.request.GET.get('scr')

        #エラー確認ボタンの送信先URLを作成
        send_url = self.request.path
        if self.request.GET.get('show_allerrors'):
            send_url += "?show_allerrors=true&"
        else:
            send_url += "?"
        context['send_url'] = send_url

        if(self.request.user.is_superuser):
            #生成ボタンの表示。過去に生成したスケジュールで最新のものを取得
            sche_newest = Schedule.objects.filter(def_sche__isnull=False).aggregate(Max('start_date'))
            sche_newest= localtime(sche_newest['start_date__max'])
            context['disp_import_thismonth'] = False
            if sche_newest < now_month:
                context['disp_import_thismonth'] = True

            context['disp_import_nextmonth'] = False
            if sche_newest < now_nextmonth:
                context['disp_import_nextmonth'] = True

            #登録ヘルパーへの表示最終日時
            show_enddate = datetime.datetime(1970,1,1)
            show_enddate = make_aware(show_enddate)
            if ShowUserEnddate.objects.all():
                show_enddate = ShowUserEnddate.objects.first().end_date
                show_enddate = localtime(show_enddate)
        
            this_month_end_time = now_nextmonth - datetime.timedelta(seconds=1)#当月末日
            next_month_end_time = now_nextmonth + relativedelta(months=1) - datetime.timedelta(seconds=1)#翌月末日
            
            context['disp_showstaff_thismonth'] = False
            if show_enddate < this_month_end_time:
                context['disp_showstaff_thismonth'] = True

            context['disp_showstaff_nextmonth'] = False
            if show_enddate < next_month_end_time:
                context['disp_showstaff_nextmonth'] = True

        #追加依頼
        context['add_request'] = AddRequest.objects.filter(confirmed_by__isnull=True).order_by('-created_at')   

        #利用者の絞込み検索用リスト
        careuser_obj = CareUser.objects.filter(is_active=True).order_by('last_kana','first_kana')
        context['careuser_obj'] = furigana_index_list(careuser_obj,"careusers")
        
        #利用者が選択されている場合
        selected_careuser = None
        context['selected_careuser'] = ""
        condition_careuser = Q()
        if self.request.GET.get('careuser'):
            selected_careuser = CareUser.objects.get(pk=int(self.request.GET.get('careuser')))
            context['selected_careuser'] = selected_careuser
            condition_careuser = Q(careuser=selected_careuser)
        
        #当月のスケジュール
        #実績入力の有無に関わらず月間のスケジュールをすべて取得
        now      = make_aware(datetime.datetime.now())

        queryset = Schedule.objects.select_related('report','service').filter(condition_careuser,start_date__range=[this_month,next_month],cancel_flg=False).order_by('report__service_in_date','start_date')
        context['this_she_cnt'] = queryset.count()

        #実績の有無でスケジュールを分別
        sche_list_is_confirmed=[]
        sche_list_not_confirmed=[]
        for sche in queryset:
            if sche.report.careuser_confirmed:
                sche_list_is_confirmed.append(sche)
            elif sche.start_date < now:
                sche_list_not_confirmed.append(sche)
                
        context['report_is_confirmed_cnt']  = len(sche_list_is_confirmed)
        context['report_not_confirmed_cnt'] = len(sche_list_not_confirmed)

        #querysetにフィルターを掛けると新たにクエリが実行されるため、上記を使用
        error_list = []
        for sche in queryset:
            if sche.report.error_code >0 and sche.report.error_code<90 or sche.report.warnings != "" or sche.report.communicate != "" or sche.biko != "": #稼働後は <90 を除外して右に戻す　or sche.report.careuser_confirmed == False:
                sche.service.kind = sche.service.get_kind_display()[:2]#サービス種別を頭２文字のみとする
                if self.request.GET.get('show_allerrors'):
                    error_list.append(sche)
                else:
                    if not sche.report.error_warn_allowed:
                        error_list.append(sche)
        context['error_list'] = error_list

        #翌月のスケジュール
        queryset = Schedule.objects.select_related('report').filter(condition_careuser,start_date__range=[next_month,next_2month],cancel_flg=False)
        context['next_she_cnt'] = queryset.count()

        return context

def furigana_index_list(obj,list_genre):

    hiragana_list =(('あ','い','う','え','お'),('か','き','く','け','こ','が','ぎ','ぐ','げ','ご'),('さ','し','す','せ','そ','ざ','じ','ず','ぜ','ぞ'),
                   ('た','ち','つ','て','と','だ','ぢ','づ','で','ど'),('な','に','ぬ','ね','の'),('は','ひ','ふ','へ','ほ','ば','び','ぶ','べ','ぼ'),
                   ('ま','み','む','め','も'),('や','ゆ','よ'),('わ','を','ん'))

    name_search_flg=[False] * 10
    
    for cu in obj:
        if (list_genre == "staffs" and cu.is_staff ==False) or (list_genre == "careusers"):
            for index,hira in enumerate(hiragana_list):
                if cu.last_kana[0:1] in hira:
                    if not name_search_flg[index]:
                        cu.last_name = hira[0] + "　" + cu.last_name
                        name_search_flg[index]=True
                    else:
                        cu.last_name = "　　" + cu.last_name
                    break
                
    return obj

def search_staff_tr_query(staff):
    cond = (Q(staff1=staff)|Q(staff2=staff)|Q(staff3=staff)|Q(staff4=staff)|Q(tr_staff1=staff)|Q(tr_staff2=staff)|Q(tr_staff3=staff)|Q(tr_staff4=staff))
    return cond

def search_relate_staff_tr_query(staff):
    cond = (Q(schedule__staff1=staff)|Q(schedule__staff2=staff)|Q(schedule__staff3=staff)|Q(schedule__staff4=staff)|Q(schedule__tr_staff1=staff)|Q(schedule__tr_staff2=staff)|Q(schedule__tr_staff3=staff)|Q(schedule__tr_staff4=staff))
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

def line_send(message):

    api_url = "https://notify-api.line.me/api/notify"
    send_contents = message
    TOKEN_dic = {'Authorization': 'Bearer' + ' ' + settings.LINE_TOKEN} 
    send_dic = {'message': send_contents}
    r = requests.post(api_url, headers=TOKEN_dic, params=send_dic)

def repo_check_errors(report,schedule):

    error_code=0

    if not report.service_out_date or not report.service_in_date:
        error_code=90
    else:
        ope_time  = math.ceil((report.service_out_date - report.service_in_date).seconds/60) #サービス総時間(分)

        def_time      = schedule.service.time
        min_time      = schedule.service.min_time

        #サービス混合の場合
        mix_items     = schedule.service.mix_items
        def_time_main = schedule.service.in_time_main
        min_time_main = schedule.service.min_time_main
        def_time_sub  = schedule.service.in_time_sub
        min_time_sub  = schedule.service.min_time_sub
        if mix_items:
            min_time = min_time_main + min_time_sub

        if report.service_in_date >= report.service_out_date:
            error_code=11
        elif mix_items == True and ope_time != report.in_time_main + report.in_time_sub:
            error_code=12  
        elif ope_time < min_time or (mix_items and (report.in_time_main < min_time_main or report.in_time_sub < min_time_sub)):
            error_code=13
        elif ope_time - def_time >15:
            error_code=14

    return error_code

def repo_check_warnings(report,schedule):
    
    warning = ""

    if report.service_out_date and report.service_in_date:
        ope_time  = math.ceil((report.service_out_date - report.service_in_date).seconds/60) #サービス総時間(分)

        if schedule.start_date <= report.service_in_date:#スタート時間との乖離
            deviation = (report.service_in_date - schedule.start_date).seconds/60
        else:    
            deviation = (schedule.start_date - report.service_in_date).seconds/60

        def_time      = schedule.service.time
        min_time      = schedule.service.min_time

        #サービス混合の場合
        mix_items     = schedule.service.mix_items
        def_time_main = schedule.service.in_time_main
        min_time_main = schedule.service.min_time_main
        def_time_sub  = schedule.service.in_time_sub
        min_time_sub  = schedule.service.min_time_sub
        if mix_items:
            min_time = min_time_main + min_time_sub
        
        #開始時間・終了時間の前後２時間以内に同一のkindで他の実績がないかチェック
        ser_in_before_2h = report.service_in_date  - datetime.timedelta(minutes = 120)
        ser_out_after_2h = report.service_out_date + datetime.timedelta(minutes = 120)

        #前後に繋がるスケジュールの存在をチェック
        err_2h_flg = False
        check_query = Schedule.objects.select_related('report','service').filter((Q(report__service_in_date__range=[ser_in_before_2h,ser_out_after_2h]) | Q(report__service_out_date__range=[ser_in_before_2h,ser_out_after_2h])),careuser=schedule.careuser,service__kind=schedule.service.kind,cancel_flg=False,report__careuser_confirmed=True).exclude(id=schedule.id)
        if check_query:
            is_before_relate = False
            is_before_report = False
            is_after_relate  = False
            is_after_report  = False

            #繋がっている予定（0時やスタッフ交代等）を除外する
            for chk in check_query:
                #サービス名から分数などの数字（時間）を取り除いたものを比較し、同一のサービスかをチェック
                check_srv_name = ''.join([i for i in chk.service.title if not i.isdigit()])
                srv_name       = ''.join([i for i in schedule.service.title if not i.isdigit()])
                #実績自体と繋がる前後の実績があれば除外する（各々のスケジュールでチェックを掛けるため、チェックしている実績の前後で繋がる実際さえあればOK）
                #beforeのチェック
                if chk.report.service_out_date <= report.service_in_date:
                    if chk.report.service_out_date == report.service_in_date and check_srv_name==srv_name:
                        is_before_relate = True
                    is_before_report = True

                #afterのチェック
                if chk.report.service_in_date >= report.service_out_date:
                    if chk.report.service_in_date == report.service_out_date and check_srv_name==srv_name:
                        is_after_relate = True
                    is_after_report = True

            if (is_before_relate is False and is_before_report) or (is_after_relate is False and is_after_report):
                err_2h_flg = True


        if err_2h_flg:
            warning += "2時間以内に他サービス有り"
        elif schedule.staff_check_level == 2:
            if warning == "": warning += " "
            warning += "スタッフ必要人数不足"
        elif schedule.staff_check_level == 3:
            if warning == "": warning += " "
            warning += "スタッフ時間重複"
        elif ope_time != def_time:
            if warning == "": warning += " "
            warning += "実績合計時間が予定と不一致"
        elif mix_items and (report.in_time_main != def_time_main or report.in_time_sub != def_time_sub):
            if warning == "": warning += " "
            warning += "内訳時間が予定と不一致"
        elif deviation >=31:
            if warning == "": warning += " "
            warning += "開始時間が31分以上乖離"
        elif schedule.careuser_check_level == 3:
            if warning == "": warning += " "
            warning += "利用者スケジュール時間重複"

    return warning

def report_for_output(rep):
    #サービス情報
    conf={}
    conf["pk"]=rep.pk
    conf["careuser"]=rep.schedule.careuser
    staffs=[]
    if rep.schedule.staff1:staffs.append(str(rep.schedule.staff1))
    if rep.schedule.staff2:staffs.append(str(rep.schedule.staff2))
    if rep.schedule.staff3:staffs.append(str(rep.schedule.staff3))
    if rep.schedule.staff4:staffs.append(str(rep.schedule.staff4))
    tr_staffs=[]
    if rep.schedule.tr_staff1:tr_staffs.append(str(rep.schedule.tr_staff1))
    if rep.schedule.tr_staff2:tr_staffs.append(str(rep.schedule.tr_staff2))
    if rep.schedule.tr_staff3:tr_staffs.append(str(rep.schedule.tr_staff3))
    if rep.schedule.tr_staff4:tr_staffs.append(str(rep.schedule.tr_staff4))

   
    conf["staffs"]              = staffs
    conf["tr_staffs"]           = tr_staffs
    conf["peoples"]             = rep.schedule.peoples
    conf["date"]                = rep.schedule.start_date
    conf["service_in_date"]     = rep.service_in_date
    conf["service_out_date"]    = rep.service_out_date
    conf["mix_reverse"]         = rep.mix_reverse
    conf["in_time_main"]        = rep.in_time_main
    conf["in_time_sub"]         = rep.in_time_sub
    conf["service"]             = rep.schedule.service.user_title
    conf["first"]               = rep.first
    conf["emergency"]           = rep.emergency
    conf["error_code"]          = rep.error_code
    conf["communicate"]         = rep.communicate
    conf["careuser_confirmed"]  = rep.careuser_confirmed

    #事前チェック
    pre_check=[]
    if rep.face_color:pre_check.append("顔色:" + rep.get_face_color_display())
    if rep.hakkan:pre_check.append("発汗:" + rep.get_hakkan_display())
    if rep.body_temp:pre_check.append("体温:" + str(rep.body_temp) + "℃")
    if rep.blood_pre_h and rep.blood_pre_l:pre_check.append("血圧:" + str(rep.blood_pre_h) + "/" + str(rep.blood_pre_l))

    #身体
    excretion=[]
    if rep.toilet:excretion.append("トイレ介助")
    if rep.p_toilet:excretion.append("Pトイレ介助")
    if rep.diapers:excretion.append("おむつ・パッド交換")
    if rep.pads:excretion.append("パッド確認")
    if rep.nyouki:excretion.append("尿器介助・洗浄")
    if rep.linen:excretion.append("リネン等処理")
    if rep.inbu:excretion.append("陰部清潔")
    
    if rep.urination_t:excretion.append("排尿回数:" + str(rep.urination_t) + "回")
    if rep.urination_a:excretion.append("排尿量:" + str(rep.urination_a) + "cc")
    if rep.defecation_t:excretion.append("排便回数:" + str(rep.defecation_t) + "回")
    if rep.defecation_s:excretion.append("排便状態:" + rep.defecation_s)
    eating=[]
    if rep.posture:eating.append("姿勢の確保")
    if rep.eating:eating.append("摂食介助:" + rep.get_eating_display())
    if rep.eat_a:eating.append("食事量:" + str(rep.eat_a) + "%")
    if rep.drink_a:eating.append("水分補給:" + str(rep.drink_a) + "cc")
    bath=[]
    if rep.bedbath:bath.append("清拭:" + rep.get_bedbath_display())
    if rep.bath:bath.append("入浴:" + rep.get_bath_display())
    if rep.wash_hair:bath.append("洗髪")
    beauty=[]
    if rep.wash_face:beauty.append("洗面")
    if rep.wash_mouse:beauty.append("口腔ケア")
    if rep.change_cloth:beauty.append("更衣介助")
    if rep.makeup_nail:beauty.append("整容（爪）")
    if rep.makeup_ear:beauty.append("整容（耳）")
    if rep.makeup_nose:beauty.append("整容（鼻）")
    if rep.makeup_hair:beauty.append("整容（髪）")
    if rep.makeup_beard:beauty.append("整容（髭）")    
    if rep.makeup_face:beauty.append("整容（化粧）")
    moving=[]
    if rep.change_pos:moving.append("体位変換")
    if rep.movetransfer:moving.append("移乗介助")
    if rep.move:moving.append("移動介助")
    if rep.readytomove:moving.append("外出準備介助")
    if rep.readytocome:moving.append("帰宅受入介助")
    if rep.gotohospital:moving.append("通院介助")
    if rep.gotoshopping:moving.append("買物介助")
    sleeping=[]
    if rep.wakeup:sleeping.append("起床介助")
    if rep.goingtobed:sleeping.append("就寝介助")
    medicine=[]
    if rep.medicine:medicine.append("服薬介助・確認")
    if rep.medicine_app:medicine.append("薬の塗布")
    if rep.eye_drops:medicine.append("点眼")
    other=[]
    if rep.in_hospital:other.append("院内介助")
    if rep.watch_over:other.append("見守り")
    independence=[]
    if rep.jir_together:independence.append("共に行う(内容):" + rep.jir_together)
    if rep.jir_memory:independence.append("記憶への働きかけ")
    if rep.jir_call_out:independence.append("声かけと見守り")
    if rep.jir_shopping:independence.append("買物援助")
    if rep.jir_motivate:independence.append("意欲関心の引き出し")
    #生活
    cleaning=[]
    if rep.cl_room:cleaning.append("居室")
    if rep.cl_toilet:cleaning.append("トイレ")
    if rep.cl_table:cleaning.append("卓上")
    if rep.cl_kitchen:cleaning.append("台所")
    if rep.cl_bath:cleaning.append("浴室")
    if rep.cl_p_toilet:cleaning.append("Pトイレ")
    if rep.cl_bedroom:cleaning.append("寝室")
    if rep.cl_hall:cleaning.append("廊下")
    if rep.cl_front:cleaning.append("玄関")
    if rep.cl_trush:cleaning.append("ゴミ出し")
    washing=[]
    if rep.washing:washing.append("洗濯")
    if rep.wash_dry:washing.append("乾燥(物干し)")
    if rep.wash_inbox:washing.append("取り入れ・収納")
    if rep.wash_iron:washing.append("アイロン")
    bedding=[]
    if rep.bed_change:bedding.append("シーツ・カバー交換")
    if rep.bed_making:bedding.append("ベッドメイク")
    if rep.bed_dry:bedding.append("布団干し")
    clothes=[]
    if rep.cloth_sort:clothes.append("衣類の整理")
    if rep.cloth_repair:clothes.append("被服の補修")
    cooking=[]
    if rep.cooking:cooking.append("調理")
    if rep.cook_lower:cooking.append("下拵え")
    if rep.cook_prepare:cooking.append("配・下膳")
    if rep.cook_menu:cooking.append("献立:" + rep.cook_menu)
    shopping=[]
    if rep.daily_shop:shopping.append("日常品等買物")
    if rep.receive_mad:shopping.append("薬の受取り")
    if rep.deposit or rep.payment:
        depo  = int(rep.deposit) if rep.deposit else 0
        pay   = int(rep.payment) if rep.payment else 0
        oturi = rep.deposit-rep.payment
        ot_name = "おつり"
        if oturi<0:
            oturi = -oturi
            ot_name = "請求額"
        #3桁区切りにする
        shopping.append("[預り金]" + "{:,}".format(depo) + "円－[買物]" + "{:,}".format(pay) + "円＝[" + ot_name +"]" + "{:,}".format(oturi) +"円")
    #退室確認
    after_check=[]
    if rep.after_fire:after_check.append("火元")
    if rep.after_elec:after_check.append("電気")
    if rep.after_water:after_check.append("水道")
    if rep.after_close:after_check.append("戸締り")


    #中身のあるもののみ追加
    physical = {}
    physical_list = {"排泄介助":excretion,"食事介助":eating,"清拭入浴":bath,"身体整容":beauty,"移動":moving,"起床就寝":sleeping,"服薬":medicine,"その他":other,"自立支援":independence}
    for name,item in physical_list.items():
        if item:physical[name] = item

    life = {}
    life_list     = {"清掃":cleaning,"洗濯":washing,"寝具":bedding,"衣類":clothes,"調理":cooking,"買物等":shopping}
    for name,item in life_list.items():
        if item:life[name] = item

    
    ret={"conf":conf}
    ret["pre_check"] = pre_check
    ret["physical"] = physical
    ret["life"] = life
    ret["after_check"] = after_check
    ret["destination"] = rep.destination
    ret["biko"] = rep.biko

    return ret


def make_email_message(rep):

    data = report_for_output(rep)#テキストデータで取得    

    message  = "介護ステーションはなをご利用頂きありがとうございました。\n"
    message += "下記の通り、サービスを実施致しましたのでご報告致します。\n\n"

    message += "利　用　者  : " + data['conf']['careuser'].last_name + " 様\n"
    message += "日　　　時  : " + localtime(data['conf']['service_in_date']).strftime("%Y年%m月%d日%H時%M分") + "～" + localtime(data['conf']['service_out_date']).strftime("%H時%M分") + "\n"
    
    message += "サービス名  : " 
    if data['conf']['first']:
        message += "（初回）"
    if data['conf']['emergency']:
        message += "（緊急）"
    message += str(rep.schedule.service.get_kind_display()) + " " + str(rep.schedule.service.user_title) + "\n"

    message += "担当ヘルパー: "
    for st in data['conf']['staffs']:
        message += st
    if data['conf']['tr_staffs']:
        message += "　[同行]"
        for st in data['conf']['tr_staffs']:
            message += st
    message += "\n"

    message += "サービス内容:\n"
    
    if data['pre_check']:
        message += "[ 事前チェック ]"
        for p in data['pre_check']:
            message += " " + p
        message += "\n"

    if data['physical']:
        message += "[身　体　介　護]"
        for key,val in data['physical'].items():
            message += " " + key + ":"
            for w in val:
                message += w + " "
        message += "\n"

    if data['life']:
        message += "[生　活　援　助]"
        for key,val in data['life'].items():
            message += " " + key + ":"
            for w in val:
                message += w + " "
        message += "\n"

    if data['after_check']:
        message += "[退　室　確　認]"
        for p in data['after_check']:
            message += " " + p
        message += "\n"

    if data['biko']:
        message += "[特記・連絡事項]"
        if data['destination']:
            message += " 行先：" + data['destination']
    
        message += " " + data['biko']
        message += "\n"
    

    message += "\n今後ともどうぞ宜しくお願い致します。"

    return message