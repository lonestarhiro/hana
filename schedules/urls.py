from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = "schedules"

urlpatterns = [

    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("",login_required(views.ScheduleListView.as_view()),name="list"),
    path("monthly/<int:year>/<int:month>",login_required(views.ScheduleListView.as_view()),name="monthlylist"),
    path("edit/<int:pk>/",login_required(views.ScheduleEditView.as_view()),name="edit"),
    path("new/",login_required(views.ScheduleCreateView.as_view()),name="new"),

]