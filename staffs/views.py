from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView

#@login_required
#def top(request):
#    return render(request,"staff/top.html")

class StaffListView(ListView):
    model = User
    template_name = "staff/stafflist.html"
    context_object_name = "Staffs"
    ordering = ['pk']



#handler400 ='staffs.views.handler400'
#handler403 ='staffs.views.handler403'
#handler404 ='staffs.views.handler404'
#handler500 ='staffs.views.handler500'