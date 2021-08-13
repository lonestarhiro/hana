from .models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView,TemplateView
from .forms import StaffForm
from .mixins import SuperUserRequiredMixin

#以下ログイン済みのみ表示(urlsにて制限中)
class TopView(TemplateView):
    template_name = 'staffs/top.html'


#以下superuserのみ表示（下のSuperUserRequiredMixinにて制限中）
class StaffListView(SuperUserRequiredMixin,ListView):
    model = User
    ordering = ['pk']

class StaffCreateView(SuperUserRequiredMixin,CreateView):
    model = User
    form_class = StaffForm
    #success_url = reverse_lazy('staffs:list')
    def get_success_url(self):
        return reverse_lazy('staffs:list')

class StaffEditView(SuperUserRequiredMixin,UpdateView):
    model = User
    form_class = StaffForm
    
    def get_success_url(self):
        return reverse_lazy('staffs:list')


#handler400 ='staffs.views.handler400'
#handler403 ='staffs.views.handler403'
#handler404 ='staffs.views.handler404'
#handler500 ='staffs.views.handler500'