from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def top(request):
    return render(request,"staff/top.html")




#handler400 ='staffs.views.handler400'
#handler403 ='staffs.views.handler403'
#handler404 ='staffs.views.handler404'
#handler500 ='staffs.views.handler500'