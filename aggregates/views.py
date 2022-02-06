from schedules.models import Schedule,Report
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.views.generic import TemplateView,ListView
import datetime
import math
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware,localtime
from django.urls import reverse_lazy,reverse

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
def kaigo_list(schedules):
    cu={}
    for sche in schedules:
        #careuser毎のリスト作成
        if sche.careuser not in cu:
            cu[sche.careuser]={}

        s_in_time  = localtime(sche.report.service_in_date)
        s_out_time = localtime(sche.report.service_out_date)

        #スケジュールをサービス内容と日時毎に分類
        add_title = ""
        if   s_in_time.time() >= datetime.time(18,00) and s_in_time.time() < datetime.time(22,00):
            add_title = "(夜)"
        elif s_in_time.time() >= datetime.time(6,00) and s_in_time.time() < datetime.time(8,00):
            add_title = "(夜)"
        elif s_in_time.time() >= datetime.time(0,00) and s_in_time.time() < datetime.time(6,00):
            add_title = "(深夜)"
        elif s_in_time.time() >= datetime.time(22,00) and s_in_time.time() < datetime.time(23,59,59):
            add_title = "(深夜)"
        
        if sche.peoples >1:
            add_title += "(" + str(sche.peoples) +"名)"

        obj_name = str(sche.service.bill_title) + add_title + " " + str(s_in_time.hour).zfill(2) + ":" + \
                    str(s_in_time.minute).zfill(2) + "-" + str(s_out_time.hour).zfill(2) + ":" +\
                    str(s_out_time.minute).zfill(2)
        if obj_name not in cu[sche.careuser]:
            cu[sche.careuser][obj_name] = []
            cu[sche.careuser][obj_name].append(s_in_time.day)   
        else:
            cu[sche.careuser][obj_name].append(s_in_time.day)

    return cu

def get_day_of_week_jp(datetime):
    w_list = ['月', '火', '水', '木', '金', '土', '日']
    return(w_list[datetime.weekday()])
