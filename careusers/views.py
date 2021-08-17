from .models import CareUser,DefaultSchedule
from django.shortcuts import get_object_or_404
from .mixins import StaffUserRequiredMixin,SuperUserRequiredMixin
from django.urls import reverse_lazy
from .forms import CareUserForm,DefscheduleForm,DefscheduleNewForm
from django.views.generic import CreateView, ListView, UpdateView,DetailView



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

class DefscheduleCreateView(SuperUserRequiredMixin,CreateView):
    model = DefaultSchedule
    form_class = DefscheduleNewForm

    def get_success_url(self):
        return reverse_lazy('careusers:list')

class DefscheduleEditView(SuperUserRequiredMixin,UpdateView):
    model = DefaultSchedule
    form_class = DefscheduleForm

    def get_success_url(self):
        return reverse_lazy('careusers:list')
