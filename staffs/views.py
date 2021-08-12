from .models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.shortcuts import render,get_list_or_404
from .forms import StaffForm,NewStaffForm

#@login_required
#def top(request):
#    return render(request,"staff/top.html")

"""
class StaffListView(ListView):
    model = User
    template_name = "staff/list.html"
    context_object_name = "staffs"
    ordering = ['pk']

class StaffEditView(View):
    form_class = StaffForm
    template_name = "staff/edit.html"

    def get(self,request,*args,**kwargs):
        form = self.form_class(instance=self.object.pk)
        return render(request,self.template_name,{'form':form})

    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            staff = form.save()
            return redirect("staffs:list")
        return render(request,self.template_name,{'form':form})

class StaffCreateView(View):
    form_class = StaffForm
    template_name = "staff/new.html"

    def get(self,request,*args,**kwargs):
        form = self.form_class
        return render(request,self.template_name,{'form':form})

    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            staff = form.save()
            return redirect("staffs:list")
        return render(request,self.template_name,{'form':form})
"""

class StaffCreateView(CreateView):
    model = User
    form_class = NewStaffForm
    template_name = "staff/new.html"
    success_url = reverse_lazy('staffs:list')


class StaffEditView(UpdateView):
    model = User
    form_class = StaffForm
    template_name = "staff/edit.html"
    success_url = reverse_lazy('staffs:list')


class StaffListView(ListView):
    model = User
    template_name = "staff/list.html"
    context_object_name = "staffs"
    ordering = ['pk']

def top(request):
    return render(request,'staff/top.html')


#handler400 ='staffs.views.handler400'
#handler403 ='staffs.views.handler403'
#handler404 ='staffs.views.handler404'
#handler500 ='staffs.views.handler500'