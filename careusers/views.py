from .models import CareUser,DefaultSchedule,Service
from schedules.models import Schedule
from django.shortcuts import get_object_or_404
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm,DefscheduleNewForm
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch


#以下StaffUserRequiredMixinのみ表示
class CareuserListView(StaffUserRequiredMixin,ListView):
    model = CareUser
    queryset = CareUser.objects.prefetch_related(Prefetch("defaultschedule_set",queryset=DefaultSchedule.objects.order_by('-sun','-mon','-tue','-wed','-thu','-fri','-sat','day','start_h','start_m'))).order_by('-is_active','last_kana','first_kana')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        nowtime = make_aware(datetime.datetime.today())
        year  = nowtime.year
        month = nowtime.month
        this_month  = make_aware(datetime.datetime(year,month,1))
        next_month  = this_month + relativedelta(months=1)
        next_2month = next_month + relativedelta(months=1)
        context['this_month'] = this_month
        context['next_month'] = next_month


        #今月分がインポートされているかどうか
        month_all_sche = Schedule.objects.filter(start_date__range=[this_month,next_month],def_sche__isnull=False)
        import_this_no_use = True
        if month_all_sche:
            import_this_no_use = False

        month_all_sche = Schedule.objects.filter(start_date__range=[next_month,next_2month],def_sche__isnull=False)
        import_next_no_use=True
        if month_all_sche:
            import_next_no_use = False

        import_btn_no_use = False
        if import_this_no_use and import_next_no_use:
            import_btn_no_use = True

        context['import_this_no_use'] = import_this_no_use
        context['import_next_no_use'] = import_next_no_use
        context['import_btn_no_use']  = import_btn_no_use

        context['tag_a']  = ['あ','い','う','え','お']
        context['tag_ka'] = ['か','き','く','け','こ','が','ぎ','ぐ','げ','ご']
        context['tag_sa'] = ['さ','し','す','せ','そ','ざ','じ','ず','ぜ','ぞ']
        context['tag_ta'] = ['た','ち','つ','て','と','だ','ぢ','づ','で','ど']
        context['tag_na'] = ['な','に','ぬ','ね','の','','','','','']
        context['tag_ha'] = ['は','ひ','ふ','へ','ほ','ば','び','ぶ','べ','ぼ']
        context['tag_ma'] = ['ま','み','む','め','も']
        context['tag_ya'] = ['や','ゆ','よ']
        context['tag_ra'] = ['ら','り','る','れ','ろ']
        context['tag_wa'] = ['わ','を','ん']

        return context

class CareuserCreateView(SuperUserRequiredMixin,CreateView):
    model = CareUser
    form_class = CareUserForm
 
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class CareuserEditView(SuperUserRequiredMixin,UpdateView):
    model = CareUser
    form_class = CareUserForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #利用中でなくなった場合は、先のスケジュールすべてキャンセルにしスタッフを外す
        if self.object.is_active is False:
            nowtime  = make_aware(datetime.datetime.now())
            cxl_sche_obj = Schedule.objects.filter(start_date__gte=nowtime,careuser=self.object)
            cxl_sche_obj.update(staff1=None,staff2=None,staff3=None,staff4=None,tr_staff1=None,tr_staff2=None,tr_staff3=None,tr_staff4=None,cancel_flg=True)
            
            #利用終了日時は利用停止した初回のみ追記
            if self.object.no_active_date is None:
                nowdate = make_aware(datetime.datetime.today())
                self.object.no_active_date = nowdate

        form.save()

        return super(CareuserEditView,self).form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleCreateView(StaffUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleNewForm
    template_name ="careusers/defaultschedule_new.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        careuser_obj = get_object_or_404(CareUser,pk=self.kwargs.get("careuser_id"))
        kwgs['careuser'] = careuser_obj

        return kwgs
        #以下コピペしたが動作せず　念のため保存
        #get_request = self.request.GET
        #if 'careuser' in get_request.keys():
        #    careuser_obj = DefscheduleNewForm.objects.get(pk=int(get_request["careuser_id"]))
        #    kwgs['careuser'] = careuser_obj
        #return kwgs
        
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        careuser_obj = get_object_or_404(CareUser,pk=self.kwargs.get("careuser_id"))
        careuser = careuser_obj
        context['careuser_name'] = careuser
        return context

class DefscheduleEditView(StaffUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
    template_name ="careusers/defaultschedule_edit.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleDeleteView(StaffUserRequiredMixin,DeleteView):
    model = DefaultSchedule
    template_name ="careusers/defaultschedule_delete.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')