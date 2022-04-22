from .models import Service
from django.db.models import Case, When, Value,PositiveSmallIntegerField
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
from .forms import ServiceForm
from hana.mixins import SuperUserRequiredMixin



#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class ServiceListView(SuperUserRequiredMixin,ListView):
    model = Service

    def get_queryset(self, **kwargs):
        odr_text = Case(
            When(title__startswith="身体", then=Value(0)),
            When(title__startswith="生活", then=Value(1)),
            When(title__startswith="家事", then=Value(2)),
            When(title__startswith="重度", then=Value(3)),
            When(title__startswith="通院", then=Value(4)),
            When(title__icontains="身有", then=Value(5)),
            When(title__icontains="身無", then=Value(6)),
            default=Value(9),
            output_field=PositiveSmallIntegerField()
        )
        query = self.model.objects.annotate(odr_text=odr_text).order_by('-is_active','kind','odr_text','time')
        return query

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
    template_name ="services/service_delete.html"

    def get_success_url(self):
        return reverse_lazy('services:list')