
from django.contrib.auth import views
from django.urls import path
from .views import StaffListView,StaffEditView,StaffCreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


app_name = "staffs"

urlpatterns = [
    path("login/",views.LoginView.as_view(redirect_authenticated_user=True,template_name="staffs/login.html"),name="login"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
    path("password_reset/", views.PasswordResetView.as_view(template_name="staffs/password_reset.html",email_template_name = 'staffs/password_reset_email.html',success_url = reverse_lazy('staffs:password_reset_done')), name="password_reset"),
    path("password_reset/done/", views.PasswordResetDoneView.as_view(template_name="staffs/password_reset_done.html"), name="password_reset_done"),
    path("password_reset/confirm/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(template_name="staffs/password_reset_confirm.html",success_url = reverse_lazy('staffs:password_reset_complete')), name="password_reset_confirm"),
    path("password_reset/complete/", views.PasswordResetCompleteView.as_view(template_name="staffs/password_reset_complete.html"), name="password_reset_complete"),


    #ログイン済みの場合のみ
    path("password_change/",login_required(views.PasswordChangeView.as_view(template_name="staffs/password_change.html",success_url = reverse_lazy('staffs:password_change_done'))),name="password_change"),
    path("password_change/done/",login_required(views.PasswordChangeDoneView.as_view(template_name="staffs/password_change_done.html")),name="password_change_done"),
    
    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("list/",login_required(StaffListView.as_view()),name="list"),
    path("list/edit/<int:pk>/",login_required(StaffEditView.as_view()),name="edit"),
    path("list/new/",login_required(StaffCreateView.as_view()),name="new"),
]
