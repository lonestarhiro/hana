from schedules.models import Schedule,Report
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.views.generic import TemplateView,ListView
from django.http import HttpResponse,Http404
from django.utils.timezone import make_aware,localtime
from django.core import serializers
import json
import datetime
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

        queryset = Schedule.objects.select_related('report','careuser','service').filter(service__kind=kind,report__careuser_confirmed=True,\
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
        new_obj['staff1']    = sche.staff1.last_name
        new_obj['staff2']    = sche.staff2.last_name
        new_obj['staff3']    = sche.staff3.last_name
        new_obj['staff4']    = sche.staff4.last_name

        cu[careuser_name].append(new_obj)

    return cu


def get_day_of_week_jp(datetime):
    w_list = ['月', '火', '水', '木', '金', '土', '日']
    return(w_list[datetime.weekday()])
