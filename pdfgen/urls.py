from django.urls import register_converter,path
from schedules import path_converter
from . import views
from django.contrib.auth.decorators import login_required

app_name = "pdfgen"

register_converter(path_converter.FourDigitYearConverter,'yyyy')
register_converter(path_converter.TweDigitMonthConverter,'mm')
register_converter(path_converter.TweDigitDayConverter,'dd')

urlpatterns = [

    #ログイン済みの場合のみ
    path("test/",login_required(views.index),name="index"),

    #以下はstaffuserのみアクセス可能(viewsにて制限)
    #path("month/",login_required(views.ScheduleListView.as_view()),name="thismonthlist"),

]