from .models import Service
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
from .forms import ServiceForm
from hana.mixins import SuperUserRequiredMixin



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class ServiceListView(SuperUserRequiredMixin,ListView):
    model = Service
    ordering = 'kind','time'

class ServiceCreateView(SuperUserRequiredMixin,CreateView):
    model = Service
    form_class = ServiceForm

    def get_success_url(self):
        return reverse_lazy('services:list')

class ServiceEditView(SuperUserRequiredMixin,UpdateView):
    model = Service
    form_class = ServiceForm
    
    def get_success_url(self):
        return reverse_lazy('services:list')

class ServiceDeleteView(SuperUserRequiredMixin,DeleteView):
    model = Service
    template_name ="services\service_delete.html"

    def get_success_url(self):
        return reverse_lazy('services:list')