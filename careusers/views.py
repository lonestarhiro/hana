from .models import CareUser,DefaultSchedule,Service
from django.shortcuts import get_object_or_404,render,redirect
from hana.mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm,DefscheduleNewForm
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch


#以下StaffUserRequiredMixinのみ表示
class CareuserListView(StaffUserRequiredMixin,ListView):
    model = CareUser
    queryset = CareUser.objects.prefetch_related(Prefetch("defaultschedule_set",queryset=DefaultSchedule.objects.order_by('-sun','-mon','-tue','-wed','-thu','-fri','-sat','day','start_h','start_m'))).order_by('-is_active','last_kana','first_kana')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        this_month_datetime  = datetime.datetime.today()
        next_month_datetime  = datetime.datetime(this_month_datetime.year,this_month_datetime.month,1) + relativedelta(months=1)

        context['this_month_datetime'] = this_month_datetime
        context['next_month_datetime'] = next_month_datetime

        return context

class CareuserCreateView(StaffUserRequiredMixin,CreateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class CareuserEditView(StaffUserRequiredMixin,UpdateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleCreateView(StaffUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleNewForm
    template_name ="careusers\defaultschedule_new.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')

    def get_form_kwargs(self, *args, **kwargs):
        kwgs = super().get_form_kwargs(*args, **kwargs)
        careuser_obj = get_object_or_404(CareUser,pk=self.kwargs.get("careuser_id"))
        kwgs['careuser'] = careuser_obj
        #print(kwgs['careuser'])
        return kwgs

        #以下コピペしたが動作せず　念のため保存
        #get_request = self.request.GET
        #if 'careuser' in get_request.keys():
        #    careuser_obj = DefscheduleNewForm.objects.get(pk=int(get_request["careuser_id"]))
        #    kwgs['careuser'] = careuser_obj
        #return kwgs
"""
class DefscheduleCreateView(SuperUserRequiredMixin,View):
    model = DefaultSchedule
    form_class = DefscheduleForm
    template_name ="careusers\defaultschedule_new.html"

    def get(self,request,*args,**kwargs):
        form = self.form_class()
        return render(request,self.template_name,{"form":form})
    
    def post(self,request,*args,**kwargs):
        form = DefscheduleNewForm(request.POST)
        #careuser = get_object_or_404(CareUser,pk=self.kwargs.get("careuser_id"))
        #print(careuser)　これ以降不明

        if form.is_valid():
            newschedule = form.save()
            return redirect('careusers:list')
        return render(request,self.template_name,{"form":form})
"""
class DefscheduleEditView(StaffUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
    template_name ="careusers\defaultschedule_edit.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleDeleteView(StaffUserRequiredMixin,DeleteView):
    model = DefaultSchedule
    template_name ="careusers\defaultschedule_delete.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')