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

        if self.object.deposit is None:
            self.object.deposit = 0;
        
        if self.object.payment is None:
            self.object.payment = 0;
        
        form.save()
        return super(ReportUpdateView,self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('schedules:report_detail',kwargs={'pk':self.object.pk})

class ReportDetailView(DetailView):
    model = Report
    template_name = "schedules/report_detail.html"

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

        context['report'] = self.report_for_output(schedule_data)
        return context

    def report_for_output(self,schedule_data):
        
        obj={}
        obj['pk'] = schedule_data.schedule.pk #pk
        obj['careuser'] = schedule_data.schedule.careuser #利用者名
        #サービススタッフ
        txt=""
        if schedule_data.schedule.peoples is 1:
            txt += str(schedule_data.schedule.staff1)
        elif schedule_data.schedule.peoples is 2:
            txt += str(schedule_data.schedule.staff1) + " " + str(schedule_data.schedule.staff2)
        elif schedule_data.schedule.peoples is 3:
            txt += str(schedule_data.schedule.staff1) + " " + str(schedule_data.schedule.staff2) + " " + str(schedule_data.schedule.staff3)
        elif schedule_data.schedule.peoples is 4:
            txt += str(schedule_data.schedule.staff1) + " " + str(schedule_data.schedule.staff2) + " " + str(schedule_data.schedule.staff3) + " " + str(schedule_data.schedule.staff4)
        if schedule_data.schedule.tr_staff1:
            txt += " [同行] " + str(schedule_data.schedule.tr_staff1)
        if schedule_data.schedule.tr_staff2:
            txt += " " + str(schedule_data.schedule.tr_staff2)
        if schedule_data.schedule.tr_staff3:
            txt += " " + str(schedule_data.schedule.tr_staff3)
        if schedule_data.schedule.tr_staff4:
            txt += " " + str(schedule_data.schedule.tr_staff4)  
        obj['helper'] = txt
        obj['date'] = schedule_data.schedule.start_date #予定日時
        obj['service_in_date']  = schedule_data.service_in_date #サービス開始日時
        obj['service_out_date'] = schedule_data.service_out_date #サービス終了日時
        obj['service'] = schedule_data.schedule.service
        obj['first'] = schedule_data.first #初回加算
        obj['emergency'] = schedule_data.emergency #緊急加算
        #事前チェック
        obj['pre_check'] = None
        if schedule_data.face_color or schedule_data.hakkan or schedule_data.body_temp or (schedule_data.blood_pre_h and schedule_data.blood_pre_l):
            txt = ""
            txt += "顔色:" + schedule_data.get_face_color_display() + "　" if schedule_data.face_color else ""
            txt += "発汗:" + schedule_data.get_hakkan_display() + "　" if schedule_data.hakkan else ""
            txt += "体温:" + str(schedule_data.body_temp) + "℃　" if schedule_data.body_temp else ""
            txt += "血圧:" + str(schedule_data.blood_pre_h) + "/" + str(schedule_data.blood_pre_l) if schedule_data.blood_pre_h and schedule_data.blood_pre_l else ""
            obj['pre_check'] = txt
        #排泄
        obj['excretion'] = None
        if schedule_data.toilet or schedule_data.p_toilet or schedule_data.Diapers or schedule_data.Pads or schedule_data.linen or schedule_data.inbu \
            or schedule_data.nyouki or schedule_data.urination_t  or schedule_data.urination_a or schedule_data.defecation_t or schedule_data.defecation_s: 
            txt = ""
            txt += "トイレ介助　"   if schedule_data.toilet   else ""
            txt += "Pトイレ介助　"  if schedule_data.p_toilet else ""
            txt += "おむつ交換　"   if schedule_data.Diapers  else ""
            txt += "パッド交換　"   if schedule_data.Pads     else ""
            txt += "リネン等処理　" if schedule_data.linen    else ""
            txt += "陰部清潔　"     if schedule_data.inbu     else ""
            txt += "尿器洗浄　"     if schedule_data.nyouki   else ""
            txt += "排尿回数:" + str(schedule_data.urination_t) + "回　"  if schedule_data.urination_t else ""
            txt += "排尿量:" + str(schedule_data.urination_a) + "cc　"    if schedule_data.urination_a else ""
            txt += "排便回数:" + str(schedule_data.defecation_t) + "回　" if schedule_data.defecation_t else ""
            txt += "排便状態:" + schedule_data.defecation_s if schedule_data.defecation_s else ""
            obj['excretion'] = txt
        #食事
        obj['eating'] = None
        if schedule_data.posture or schedule_data.eating or schedule_data.eat_a or schedule_data.drink_a:
            txt = ""
            txt += "姿勢の確保　" if schedule_data.posture else ""
            txt += "摂食介助:" + schedule_data.get_eating_display() + "　" if schedule_data.eating  else ""
            txt += "食事量:" + str(schedule_data.eat_a) + "%　"            if schedule_data.eat_a   else ""
            txt += "水分補給:" + str(schedule_data.drink_a) + "cc　"       if schedule_data.drink_a else ""
            obj['eating'] =txt
        #清拭入浴
        obj['bath'] = None
        if schedule_data.bedbath or schedule_data.bath or schedule_data.wash_hair:
            txt = ""
            txt += "清拭:" + schedule_data.get_bedbath_display() + "　" if schedule_data.bedbath else ""
            txt += "入浴:" + schedule_data.get_bath_display() + "　"    if schedule_data.bath    else ""
            txt += "洗髪　" if schedule_data.wash_hair else ""
            obj['bath'] =txt
        #身体整容
        obj['beauty'] = None
        if schedule_data.wash_face or schedule_data.wash_mouse or schedule_data.change_cloth or schedule_data.makeup_nail or schedule_data.makeup_ear or schedule_data.makeup_beard or schedule_data.makeup_hair or schedule_data.makeup_face:
            txt = ""
            txt += "洗面　"         if schedule_data.wash_face    else ""
            txt += "口腔ケア　"     if schedule_data.wash_mouse   else ""
            txt += "更衣介助　"     if schedule_data.change_cloth else ""
            txt += "整容（爪）　"   if schedule_data.makeup_nail  else ""
            txt += "整容（耳）　"   if schedule_data.makeup_ear   else ""
            txt += "整容（髭）　"   if schedule_data.makeup_beard else ""
            txt += "整容（髪）　"   if schedule_data.makeup_hair  else ""
            txt += "整容（化粧）　" if schedule_data.makeup_face  else ""
            obj['beauty'] =txt
        #移動
        obj['moving'] = None
        if schedule_data.change_pos or schedule_data.movetransfer or schedule_data.move or schedule_data.readytomove or schedule_data.readytocome or schedule_data.gotohospital or schedule_data.gotoshopping:
            txt = ""
            txt += "体位変換　"     if schedule_data.change_pos   else ""
            txt += "移乗介助　"     if schedule_data.movetransfer else ""
            txt += "移動介助　"     if schedule_data.move         else ""
            txt += "外出準備介助　" if schedule_data.readytomove  else ""
            txt += "帰宅受入介助　" if schedule_data.readytocome  else ""
            txt += "通院介助　"     if schedule_data.gotohospital else ""
            txt += "買物介助　"     if schedule_data.gotoshopping else ""
            obj['moving'] =txt
        #起床就寝
        obj['sleeping'] = None
        if schedule_data.wakeup or schedule_data.goingtobed:
            txt = ""
            txt += "起床介助　" if schedule_data.wakeup     else ""
            txt += "就寝介助　" if schedule_data.goingtobed else ""
            obj['sleeping'] =txt
        #服薬
        obj['medicine'] = None
        if schedule_data.medicine or schedule_data.medicine_app or schedule_data.eye_drops:
            txt = ""
            txt += "服薬介助・確認　" if schedule_data.medicine     else ""
            txt += "薬の塗布　"       if schedule_data.medicine_app else ""
            txt += "点眼　"           if schedule_data.eye_drops    else ""
            obj['medicine'] =txt
        #その他
        obj['other'] = None
        if schedule_data.in_hospital or schedule_data.watch_over:
            txt = ""
            txt += "院内介助　" if schedule_data.in_hospital else ""
            txt += "見守り　"   if schedule_data.watch_over  else ""
            obj['other'] =txt
        #自立支援
        obj['independence'] = None
        if schedule_data.jir_together or schedule_data.jir_memory or schedule_data.jir_call_out or schedule_data.jir_shopping or schedule_data.jir_motivate:
            txt = ""
            txt += "共に行う(内容):" + schedule_data.jir_together + "　" if schedule_data.jir_together else ""
            txt += "記憶への働きかけ　"   if schedule_data.jir_memory   else ""
            txt += "声かけと見守り　"     if schedule_data.jir_call_out else ""
            txt += "買物援助　"           if schedule_data.jir_shopping else ""
            txt += "意欲関心の引き出し　" if schedule_data.jir_motivate else ""
            obj['independence'] =txt
        #清掃
        obj['cleaning'] = None
        if schedule_data.cl_room or schedule_data.cl_toilet or schedule_data.cl_table or schedule_data.cl_kitchen or schedule_data.cl_bath or schedule_data.cl_p_toilet or schedule_data.cl_bedroom or schedule_data.cl_hall or schedule_data.cl_front or schedule_data.cl_trush:
            txt = ""
            txt += "居室　"     if schedule_data.cl_room     else ""
            txt += "トイレ　"   if schedule_data.cl_toilet   else ""
            txt += "卓上　"     if schedule_data.cl_table    else ""
            txt += "台所　"     if schedule_data.cl_kitchen  else ""
            txt += "浴室　"     if schedule_data.cl_bath     else ""
            txt += "Pトイレ　"  if schedule_data.cl_p_toilet else ""
            txt += "寝室　"     if schedule_data.cl_bedroom  else ""
            txt += "廊下　"     if schedule_data.cl_hall     else ""
            txt += "玄関　"     if schedule_data.cl_front    else ""
            txt += "ゴミ出し　" if schedule_data.cl_trush    else ""
            obj['cleaning'] =txt
        #洗濯
        obj['washing'] = None
        if schedule_data.washing or schedule_data.wash_dry or schedule_data.wash_inbox or schedule_data.wash_iron:
            txt = ""
            txt += "洗濯　"           if schedule_data.washing    else ""
            txt += "乾燥(物干し)　"   if schedule_data.wash_dry   else ""
            txt += "取り入れ・収納　" if schedule_data.wash_inbox else ""
            txt += "アイロン　"       if schedule_data.wash_iron  else ""
            obj['washing'] =txt
        #寝具
        obj['bedding'] = None
        if schedule_data.bed_change or schedule_data.bed_making or schedule_data.bed_dry:
            txt = ""
            txt += "シーツ・カバー交換　" if schedule_data.bed_change else ""
            txt += "ベッドメイク　"       if schedule_data.bed_making else ""
            txt += "布団干し　"           if schedule_data.bed_dry    else ""
            obj['bedding'] =txt
        #衣類
        obj['clothes'] = None
        if schedule_data.cloth_sort or schedule_data.cloth_repair:
            txt = ""
            txt += "衣類の整理　" if schedule_data.cloth_sort   else ""
            txt += "被服の補修　" if schedule_data.cloth_repair else ""
            obj['clothes'] =txt
        #調理
        obj['cooking'] = None
        if schedule_data.cooking or schedule_data.cook_lower or schedule_data.cook_prepare or schedule_data.cook_menu:
            txt = ""
            txt += "調理　"     if schedule_data.cooking      else ""
            txt += "下拵え　"   if schedule_data.cook_lower   else ""
            txt += "配・下膳　" if schedule_data.cook_prepare else ""
            txt += "献立:" + schedule_data.cook_menu + "　" if schedule_data.cook_menu  else ""
            obj['cooking'] =txt
        #買物等
        obj['shopping'] = None
        if schedule_data.daily_shop or schedule_data.Receive_mad or schedule_data.deposit or schedule_data.payment:
            txt = ""
            txt += "日常品等買物　"     if schedule_data.daily_shop      else ""
            txt += "薬の受取り　"   if schedule_data.Receive_mad   else ""
            if schedule_data.deposit or schedule_data.payment:
                depo  = "{:,}".format(schedule_data.deposit)#3桁区切りにする
                pay   = "{:,}".format(schedule_data.payment)#3桁区切りにする
                oturi = "{:,}".format(schedule_data.deposit-schedule_data.payment)#3桁区切りにする
                txt += "預り金:" + depo + "円－買物:" + pay + "円＝おつり:" + oturi +"円　"
            obj['shopping'] =txt
        #備考
        obj['biko'] = schedule_data.biko
        #退室確認
        obj['after_check'] = None
        if schedule_data.after_fire or schedule_data.after_elec or schedule_data.after_water or schedule_data.after_close:
            txt = ""
            txt += "火元　"   if schedule_data.after_fire  else ""
            txt += "電気　"   if schedule_data.after_elec  else ""
            txt += "水道　"   if schedule_data.after_water else ""
            txt += "戸締り　" if schedule_data.after_close else ""
            obj['after_check'] =txt

        #身体・生活それぞれの登録があるかどうか
        obj['is_physical_care'] = False
        obj['is_life_support']  = False
        if obj['excretion'] or obj['eating'] or obj['bath'] or obj['beauty'] or obj['moving'] \
             or obj['sleeping'] or obj['medicine'] or obj['other'] or obj['independence']:
            obj['is_physical_care'] = True
        if obj['cleaning'] or obj['washing'] or obj['bedding'] or obj['clothes'] or obj['cooking'] or obj['shopping']:
            obj['is_life_support'] = True

        return obj

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
    