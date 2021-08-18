from django.urls import path
from careusers import views
from django.contrib.auth.decorators import login_required

app_name = "careusers"

urlpatterns = [

    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("list/",login_required(views.CareuserListView.as_view()),name="list"),
    path("list/edit/<int:pk>/",login_required(views.CareuserEditView.as_view()),name="edit"),
    path("list/new/",login_required(views.CareuserCreateView.as_view()),name="new"),

    path("def_schedule/edit/<int:pk>/",login_required(views.DefscheduleEditView.as_view()),name="def_sche_edit"),
    path("def_schedule/new/<int:careuser_id>",login_required(views.DefscheduleCreateView.as_view()),name="def_sche_new"),
    path("def_schedule/delete/<int:pk>/",login_required(views.DefscheduleDeleteView.as_view()),name="def_sche_delete"),
]