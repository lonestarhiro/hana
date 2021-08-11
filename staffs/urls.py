
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import path


app_name = "staffs"

urlpatterns = [
    path('',LoginView.as_view(redirect_authenticated_user=True,template_name="staff/login.html"),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('top/',LoginView.as_view(template_name="staff/top.html"),name='top'),
]
