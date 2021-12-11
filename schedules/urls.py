from django.urls import register_converter,path
from . import path_converter
from . import views,scheduleimportviews
from django.contrib.auth.decorators import login_required

app_name = "schedules"

register_converter(path_converter.FourDigitYearConverter,'yyyy')
register_converter(path_converter.TweDigitMonthConverter,'mm')
register_converter(path_converter.TweDigitDayConverter,'dd')

urlpatterns = [

    #ログイン済みの場合のみ
    path("day/",login_required(views.ScheduleDailyListView.as_view()),name="todaylist"),
    path("daily/<yyyy:year>/<mm:month>/<dd:day>",login_required(views.ScheduleDailyListView.as_view()), name='dailylist'),
    path("calender/",login_required(views.ScheduleCalendarListView.as_view()), name='calendar'),
    path("monthlycalender/<yyyy:year>/<mm:month>",login_required(views.ScheduleCalendarListView.as_view()), name="monthlycalendar"),
    path("report/<int:pk>/",login_required(views.ReportUpdateView.as_view()),name="report"),
    path("report/detail/<int:pk>/",login_required(views.ReportDetailView.as_view()),name="report_detail"),

    #以下はstaffuserのみアクセス可能(viewsにて制限)
    path("month/",login_required(views.ScheduleListView.as_view()),name="thismonthlist"),
    path("monthly/<yyyy:year>/<mm:month>",login_required(views.ScheduleListView.as_view()),name="monthlylist"),
    path("monthly/<yyyy:year>/<mm:month>/<dd:day>",login_required(views.ScheduleListView.as_view()),name="dayselectlist"),
    path("import/",login_required(scheduleimportviews.ScheduleImportView.as_view()),name="import"),
    path("import_next/",login_required(scheduleimportviews.ScheduleImportView.as_view()),name="import_next"),
    path("edit/<int:pk>/",login_required(views.ScheduleEditView.as_view()),name="edit"),
    path("new/",login_required(views.ScheduleCreateView.as_view()),name="new"),
    path("delete/<int:pk>/",login_required(views.ScheduleDeleteView.as_view()),name="delete"),
    path("showstaff/<yyyy:year>/<mm:month>",login_required(views.ScheduleShowStaffView.as_view()),name="monthly_show_allstaff"),

]