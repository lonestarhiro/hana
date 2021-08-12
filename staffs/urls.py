
from django.contrib.auth import views
from django.urls import path
from staffs.views import StaffListView,StaffEditView,StaffCreateView,top
from django.contrib.auth.decorators import login_required


app_name = "staffs"

urlpatterns = [
    path('login/',views.LoginView.as_view(redirect_authenticated_user=True,template_name="staff/login.html"),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('password_reset/', views.PasswordResetView.as_view(template_name="staff/password_reset.html"), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(template_name="staff/password_reset_done.html"), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(template_name="staff/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetCompleteView.as_view(template_name="staff/password_reset_complete.html"), name='password_reset_complete'),


    #ログイン済みの場合のみアクセス可能
    path('',login_required(top),name='top'),
    path('password_change/',views.PasswordChangeView.as_view(template_name="staff/password_change.html"),name="password_change"),
    path('password_change/done/',views.PasswordChangeDoneView.as_view(template_name="staff/password_change_done.html"),name="password_change_done"),
    
    #以下はsuperuserのみアクセス可能にする
    path('list/',login_required(StaffListView.as_view()),name='list'),
    path('list/edit/<int:pk>/',login_required(StaffEditView.as_view()),name='edit'),
    path('list/new/',login_required(StaffCreateView.as_view()),name='new'),
]
