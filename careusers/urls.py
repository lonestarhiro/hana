from django.urls import path
from careusers import views
from django.contrib.auth.decorators import login_required

app_name = "careusers"

urlpatterns = [

    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("list/",login_required(views.CareuserListView.as_view()),name="list"),
    path("list/edit/<int:pk>/",login_required(views.CareuserEditView.as_view()),name="edit"),
    path("list/new/",login_required(views.CareuserCreateView.as_view()),name="new"),

    path("def_schedule_list/<int:careuser_id>",login_required(views.DefscheduleListView.as_view()),name="def_sche_list"),
    path("def_schedule_list/edit/<int:pk>/",login_required(views.DefscheduleUpdateView.as_view()),name="def_sche_update"),
    path("def_schedule_list/new/<int:careuser_id>",login_required(views.DefscheduleCreateView.as_view()),name="def_sche_new"),
]