
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import path
from staffs import views


app_name = "staffs"

urlpatterns = [
    path('login/',LoginView.as_view(redirect_authenticated_user=True,template_name="staff/login.html"),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('',views.top,name='top'),
    path('list/',views.StaffListView.as_view(),name='list'),
    path('list/edit/<int:pk>/',views.StaffEditView.as_view(),name='edit'),
    path('list/new/',views.StaffCreateView.as_view(),name='new'),
]
