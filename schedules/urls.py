from django.urls import register_converter,path
from . import path_converter
from . import views
from django.contrib.auth.decorators import login_required

app_name = "schedules"

register_converter(path_converter.FourDigitYearConverter,'yyyy')
register_converter(path_converter.TweDigitMonthConverter,'mm')

urlpatterns = [

    #以下はsuperuserのみアクセス可能(viewsにて制限)
    #path("",login_required(views.ScheduleListView.as_view()),name="top"),
    path("monthly/",login_required(views.ScheduleListView.as_view()),name="thismonthlist"),
    path("monthly/<yyyy:year>/<mm:month>",login_required(views.ScheduleListView.as_view()),name="monthlylist"),
    path("edit/<int:pk>/",login_required(views.ScheduleEditView.as_view()),name="edit"),
    path("new/",login_required(views.ScheduleCreateView.as_view()),name="new"),

]