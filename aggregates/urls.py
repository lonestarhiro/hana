from django.urls import register_converter,path
from schedules import path_converter
from . import views
from django.contrib.auth.decorators import login_required

app_name = "aggregates"

register_converter(path_converter.FourDigitYearConverter,'yyyy')
register_converter(path_converter.TweDigitMonthConverter,'mm')
register_converter(path_converter.TweDigitDayConverter,'dd')

urlpatterns = [
    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("top/",login_required(views.TopView.as_view()),name="aggregate_top"),
    path("invoice_kaigo/<yyyy:year>/<mm:month>",login_required(views.KaigoView.as_view()),name="invoice_kaigo"),
    path('invoice_kaigo/export/<yyyy:year>/<mm:month>',login_required(views.kaigo_export), name='kaigo_export'),
    path("invoice_sougou/<yyyy:year>/<mm:month>",login_required(views.SougouView.as_view()),name="invoice_sougou"),
    path('invoice_sougou/export/<yyyy:year>/<mm:month>',login_required(views.sougou_export), name='sougou_export'),
    path("invoice/<str:kind>/<yyyy:year>/<mm:month>",login_required(views.InvoiceView.as_view()),name="invoice"),
    path('invoice/export/<str:kind>/<yyyy:year>/<mm:month>',login_required(views.export), name='invoice_export'),
    path("salary_employee/<yyyy:year>/<mm:month>",login_required(views.SalaryEmployeeView.as_view()),name="salary_employee"),
    path('salary_employee/export/<yyyy:year>/<mm:month>',login_required(views.salalyemployee_export), name='salaly_employee_export'),
]