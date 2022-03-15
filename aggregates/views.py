from schedules.models import Schedule,Report
from schedules.views import search_staff_tr_query
from staffs.models import User
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin,jpweek
from django.views.generic import TemplateView,ListView
from django.http import HttpResponse,Http404
from django.utils.timezone import make_aware,localtime
import json
import datetime
import calendar
import math
from dateutil.relativedelta import relativedelta


class TopView(SuperUserRequiredMixin,TemplateView):
    model = Schedule
    template_name = "aggregates/aggregate_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = datetime.datetime.now()
        now = make_aware(now)
        context['time_now'] = now

        #画面推移後の戻るボタン用にpathをセッションに記録
        self.request.session['from'] = self.request.get_full_path()

        return context

class KaigoView(SuperUserRequiredMixin,ListView):
    model = Schedule
    template_name = "aggregates/invoice_kaigo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = self.kwargs.get('year')
        month= self.kwargs.get('month')
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)

        context['this_month']    = this_month
        context['next_month']    = next_month
        context['before_month']  = before_month

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=0,report__careuser_confirmed=True,\
                   report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')

        cu = kaigo_list(queryset)        
        context['careuser']  = cu

        return context

def kaigo_export(request,year,month):
    
    if request.user.is_superuser:
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=0,report__careuser_confirmed=True,\
                    report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')
        cu_data = kaigo_list(queryset)
        
        json_data =  json.dumps(cu_data,ensure_ascii=False)

        response = HttpResponse(json_data,content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="kaigo.json"'

        return response
    else:
        return Http404

def kaigo_list(schedules):
    cu={}
    for sche in schedules:
        #careuser毎のリスト作成
        careuser_name = sche.careuser.last_name + " " + sche.careuser.first_name
        if careuser_name not in cu:
            cu[careuser_name]=[]

        s_in_time  = localtime(sche.report.service_in_date)
        s_out_time = localtime(sche.report.service_out_date)

        #スケジュールをサービス内容と日時毎に分類
        service  = sche.service.bill_title
        mix_items = sche.service.mix_items
        night    = False
        midnight = False

        if   s_in_time.time() >= datetime.time(18,00) and s_in_time.time() < datetime.time(22,00):
            night = True
        elif s_in_time.time() >= datetime.time(6,00) and s_in_time.time() < datetime.time(8,00):
            night = True
        elif s_in_time.time() >= datetime.time(0,00) and s_in_time.time() < datetime.time(6,00):
            midnight = True
        elif s_in_time.time() >= datetime.time(22,00) and s_in_time.time() < datetime.time(23,59,59):
            midnight = True
        
        peoples = sche.peoples
        in_time  = str(s_in_time.hour).zfill(2) + ":" + str(s_in_time.minute).zfill(2)
        out_time = str(s_out_time.hour).zfill(2) + ":" + str(s_out_time.minute).zfill(2)        

        add_check = False

        #同日のスケジュールがあれば日付を追記
        if cu[careuser_name]:
            for sche in cu[careuser_name]:
                if sche['service'] == service and sche['night']==night and sche['midnight']==midnight and sche['peoples']==peoples and sche['in_time'] == in_time and sche['out_time'] == out_time:
                   sche['date'].append(int(s_in_time.day))
                   add_check = True
                   break

        #なければ新たなスケジュールを作成
        if not add_check:
            new_obj = {}
            new_obj['year']      = s_in_time.strftime("%Y")
            new_obj['month']     = s_in_time.strftime("%m")
            new_obj['service']   = service
            new_obj['mix_items'] = mix_items
            new_obj['night']     = night
            new_obj['midnight']  = midnight
            new_obj['peoples']   = peoples
            new_obj['in_time']   = in_time
            new_obj['out_time']  = out_time
            new_obj['date']      = [int(s_in_time.day)]

            cu[careuser_name].append(new_obj)

    return cu

class SougouView(SuperUserRequiredMixin,ListView):
    model = Schedule
    template_name = "aggregates/invoice_sougou.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = self.kwargs.get('year')
        month= self.kwargs.get('month')
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)

        context['this_month']    = this_month
        context['next_month']    = next_month
        context['before_month']  = before_month

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=3,report__careuser_confirmed=True,\
                   report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')

        cu = kaigo_list(queryset)        
        context['careuser']  = cu

        return context

def sougou_export(request,year,month):
    
    if request.user.is_superuser:
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=3,report__careuser_confirmed=True,\
                    report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')
        
        cu_data = kaigo_list(queryset)        
        json_data =  json.dumps(cu_data,ensure_ascii=False)

        response = HttpResponse(json_data,content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="sougou.json"'

        return response
    else:
        return Http404

class InvoiceView(SuperUserRequiredMixin,ListView):
    model = Schedule
    template_name = "aggregates/invoice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        kind = int(self.kwargs.get('kind'))
        context['kind'] = kind

        year = self.kwargs.get('year')
        month= self.kwargs.get('month')
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)

        context['this_month']    = this_month
        context['next_month']    = next_month
        context['before_month']  = before_month

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=kind,report__careuser_confirmed=True,\
                   report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')

        context['data']  = queryset

        return context

def export(request,kind,year,month):
    
    if request.user.is_superuser:
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)

        queryset = Schedule.objects.select_related('report','careuser','service','staff1','staff2','staff3','staff4').filter(service__kind=kind,report__careuser_confirmed=True,\
                    report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('careuser__last_kana','careuser__first_kana','report__service_in_date')

        cu_data = export_list(queryset)        
        json_data =  json.dumps(cu_data,ensure_ascii=False)

        response = HttpResponse(json_data,content_type='application/json')
        if kind == 1:
            response['Content-Disposition'] = 'attachment; filename="shougai.json"'
        elif kind == 2:
            response['Content-Disposition'] = 'attachment; filename="idou.json"'
        elif kind == 4:
            response['Content-Disposition'] = 'attachment; filename="doukou.json"'
        elif kind == 5:
            response['Content-Disposition'] = 'attachment; filename="jihi.json"'

        return response
    else:
        return Http404

def export_list(schedules):
    cu={}
    for sche in schedules:

        s_in_time  = localtime(sche.report.service_in_date)
        s_out_time = localtime(sche.report.service_out_date)

        night    = False
        midnight = False

        if   s_in_time.time() >= datetime.time(18,00) and s_in_time.time() < datetime.time(22,00):
            night = True
        elif s_in_time.time() >= datetime.time(6,00) and s_in_time.time() < datetime.time(8,00):
            night = True
        elif s_in_time.time() >= datetime.time(0,00) and s_in_time.time() < datetime.time(6,00):
            midnight = True
        elif s_in_time.time() >= datetime.time(22,00) and s_in_time.time() < datetime.time(23,59,59):
            midnight = True
        
        in_time  = str(s_in_time.hour).zfill(2) + ":" + str(s_in_time.minute).zfill(2)
        out_time = str(s_out_time.hour).zfill(2) + ":" + str(s_out_time.minute).zfill(2)        


        #careuser毎のリスト作成
        careuser_name = sche.careuser.last_name + " " + sche.careuser.first_name
        if careuser_name not in cu:
            cu[careuser_name]=[]

        new_obj = {}
        new_obj['year']      = s_in_time.year
        new_obj['month']     = s_in_time.month
        new_obj['day']       = s_in_time.day
        new_obj['service']   = sche.service.bill_title
        new_obj['mix_items'] = sche.service.mix_items
        new_obj['night']     = night
        new_obj['midnight']  = midnight
        new_obj['peoples']   = sche.peoples
        new_obj['in_time']   = in_time
        new_obj['out_time']  = out_time
        new_obj['staff1']    = sche.staff1.last_name if sche.staff1 else None
        new_obj['staff2']    = sche.staff2.last_name if sche.staff2 else None
        new_obj['staff3']    = sche.staff3.last_name if sche.staff3 else None
        new_obj['staff4']    = sche.staff4.last_name if sche.staff4 else None

        cu[careuser_name].append(new_obj)

    return cu


class SalaryEmployeeView(SuperUserRequiredMixin,ListView):
    model = Schedule
    template_name = "aggregates/salaryemployee.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = self.kwargs.get('year')
        month= self.kwargs.get('month')
        this_month   = make_aware(datetime.datetime(year,month,1))
        next_month   = this_month + relativedelta(months=1)
        before_month = this_month - relativedelta(months=1)

        context['this_month']    = this_month
        context['next_month']    = next_month
        context['before_month']  = before_month

        #スタッフ毎の実績を取得
        staffs = User.objects.filter(salary=1).order_by('-is_staff','last_kana','first_kana')
        staff_obj_list = []
        for staff in staffs:
            obj = {}
            obj['staff'] = staff

            condition_staff = search_staff_tr_query(staff)
            queryset = Schedule.objects.select_related('report','careuser','service').filter(condition_staff,report__careuser_confirmed=True,\
                       report__service_in_date__range=[this_month,next_month],cancel_flg=False).order_by('report__service_in_date')
            
            obj['schedules'] = queryset
            staff_obj_list.append(obj)

        #給与出力用にlistを生成
        achieve = achieve_list(staff_obj_list,year,month)        
        context['achieve']  = achieve

        return context

def achieve_list(staff_obj_list,year,month):

    archive = []

    for s in staff_obj_list:
        #一カ月の日数を取得(最終日のみ)
        days = calendar.monthrange(year,month)[1]
        obj ={}
        obj['staff_name'] = s['staff'].last_name + " " + s['staff'].first_name
        obj['month_total_hour'] = 0;
        obj['month_off_hour'] = 0;
        days_data = {}
        for day in range(days):
            # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
            days_data[day+1] = {}
            days_data[day+1]['week'] = jpweek(make_aware(datetime.datetime(year,month,day+1,0,0)))
            days_data[day+1]['schedules'] = []
            days_data[day+1]['day_service_hour'] = 0
            days_data[day+1]['day_move_hour'] = 0     
            days_data[day+1]['off_hours'] = 0

        for sche in s['schedules']:
            d ={}
            s_in_date  = localtime(sche.report.service_in_date)
            s_out_date = localtime(sche.report.service_out_date)
            
            d['real_minutes']  = math.floor((s_out_date - s_in_date).total_seconds()/60)
            d['real_hour']     = math.floor(d['real_minutes']/15)*0.25
            d['s_in_time']  = str(s_in_date.hour).zfill(2)  + ":" + str(s_in_date.minute).zfill(2)
            d['s_out_time'] = str(s_out_date.hour).zfill(2) + ":" + str(s_out_date.minute).zfill(2)
            d['s_in_time_datetime']  = s_in_date
            d['s_out_time_datetime'] = s_out_date

            
            d['careuser'] = sche.careuser.last_name + " " + sche.careuser.first_name
            d['service'] = ""
            if sche.service.kind==0:d['service'] += "[介護]"
            elif sche.service.kind==1:d['service'] += "[障害]"
            d['service']  += sche.service.title

            d['service_minutes']  = sche.service.time
            d['service_hour']     = math.floor(sche.service.time/15)*0.25

            #同行チェック
            d['doukou'] = False
            if sche.tr_staff1 == s['staff'] or sche.tr_staff2 == s['staff'] or sche.tr_staff3 == s['staff'] or sche.tr_staff4 == s['staff']:
                d['doukou'] = True
            

            #実質時間または規定時間を計算適用時間とする。
            if d['real_hour'] > d['service_hour']:
                d['adopt_hour'] = d['real_hour']
            else:
                d['adopt_hour'] = d['service_hour']
            #合計時間に加算する。
            days_data[s_in_date.day]['day_service_hour'] += d['adopt_hour']
            obj['month_total_hour'] += d['adopt_hour']

            #移動時間を加算
            chk_flg = False
            d['move_hour'] = 0
            for sche in days_data[s_in_date.day]['schedules']:
                if sche['careuser'] == d['careuser']:
                     #全く同じ時間の場合
                    if s_in_date==sche['s_in_time_datetime'] and s_out_date == sche['s_out_time_datetime']:
                        chk_flg = True
                    #一部が重なる場合
                    elif s_in_date < sche['s_in_time_datetime'] and s_out_date > sche['s_in_time_datetime'] and s_out_date <= sche['s_out_time_datetime']:
                        chk_flg = True
                    elif s_in_date >= sche['s_in_time_datetime'] and s_in_date < sche['s_out_time_datetime'] and s_out_date > sche['s_out_time_datetime']:
                        chk_flg = True
                    #内包する場合
                    elif s_in_date < sche['s_in_time_datetime'] and s_out_date > sche['s_out_time_datetime']:
                        chk_flg = True
                    elif s_in_date > sche['s_in_time_datetime'] and s_out_date < sche['s_out_time_datetime']:
                        chk_flg = True
                    #繋がる予定の場合
                    elif s_in_date == sche['s_out_time_datetime'] or s_out_date == sche['s_in_time_datetime']:
                        chk_flg = True
            if not chk_flg:
                d['move_hour'] = 0.25
                days_data[s_in_date.day]['day_move_hour'] += 0.25
                #合計時間に加算する。
                obj['month_total_hour'] += 0.25

            #22~5時の時間外時間を加算 #15分未満を切り捨てて時間変換（0.25を掛ける）にする
            oc5  = make_aware(datetime.datetime(s_in_date.year,s_in_date.month,s_in_date.day,5,0))
            oc22 = make_aware(datetime.datetime(s_in_date.year,s_in_date.month,s_in_date.day,22,0))
            d['off_hour'] = 0
            if s_in_date < oc5:
                if s_out_date <= oc5: d['off_hour'] += math.floor(((s_out_date - s_in_date).total_seconds()/60)/15)*0.25
                else: d['off_hour'] += math.floor(((oc5 - s_in_date).total_seconds()/60)/15)*0.25
            if s_out_date > oc22:
                if s_in_date >= oc22: d['off_hour'] += math.floor(((s_out_date - s_in_date).total_seconds()/60)/15)*0.25
                else: d['off_hour'] += math.floor(((s_out_date - oc22).total_seconds()/60)/15)*0.25

            days_data[s_in_date.day]['off_hours'] += d['off_hour']
            obj['month_off_hour'] += d['off_hour']

            #日毎のサービスと移動の合計時間を上書きセット
            days_data[s_in_date.day]['day_total_hour'] = days_data[s_in_date.day]['day_service_hour'] + days_data[s_in_date.day]['day_move_hour']

            days_data[s_in_date.day]['schedules'].append(d)

        obj['days_data'] = days_data
        archive.append(obj)

    return archive



