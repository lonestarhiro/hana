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
    path("calender/<yyyy:year>/<mm:month>",login_required(views.PrintCalendarView.as_view()),name="calendar"),

    #以下はstaffuserのみアクセス可能(viewsにて制限)
    path("monthly_report/<yyyy:year>/<mm:month>",login_required(views.PrintMonthlyReportView.as_view()),name="monthlyreport"),
    path("VisitedForm/<yyyy:year>/<mm:month>",login_required(views.PrintVisitedListFormView.as_view()),name="viditedlistform"),

]