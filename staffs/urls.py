
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import path
from . import views


app_name = "staffs"

urlpatterns = [
    path('login/',LoginView.as_view(redirect_authenticated_user=True,template_name="staff/login.html"),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('',views.top,name='top'),
]
