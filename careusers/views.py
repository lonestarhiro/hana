from .models import CareUser,DefaultSchedule
from django.shortcuts import get_object_or_404,render,redirect
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm,DefscheduleNewForm
from django.views.generic import CreateView, ListView, UpdateView,View,DeleteView



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class CareuserListView(SuperUserRequiredMixin,ListView):
    model = CareUser
    queryset = CareUser.objects.all().prefetch_related("defaultschedule_set").all()
    ordering = ['pk']

class CareuserCreateView(SuperUserRequiredMixin,CreateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')

class CareuserEditView(SuperUserRequiredMixin,UpdateView):
    model = CareUser
    form_class = CareUserForm
    
    def get_success_url(self):
        return reverse_lazy('careusers:list')
"""
class DefscheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleNewForm
    template_name ="careusers\defaultschedule_new.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')
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
        #print(careuser)
        #form.fields['careuser'] = careuser.pk

        if form.is_valid():
            newschedule = form.save()
            return redirect('careusers:list')
        return render(request,self.template_name,{"form":form})

class DefscheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    form_class = DefscheduleForm
    template_name ="careusers\defaultschedule_edit.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleDeleteView(SuperUserRequiredMixin,DeleteView):
    model = DefaultSchedule
    template_name ="careusers\defaultschedule_delete.html"

    def get_success_url(self):
        return reverse_lazy('careusers:list')