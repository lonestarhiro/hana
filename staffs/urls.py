
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import path
from .views import StaffListView


app_name = "staffs"

urlpatterns = [
    path('login/',LoginView.as_view(redirect_authenticated_user=True,template_name="staff/login.html"),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('stafflist/',StaffListView.as_view(),name='stafflist'),
]
