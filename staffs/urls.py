from django.urls import path
from staffs import views

urlpatterns = [

    path("new_staff/",views.staff_new,name="staff_new"),
    path("<int:staff_id>/",views.staff_conf,name="staff_conf"),
    path("<int:staff_id>/edit/",views.staff_edit,name="staff_edit"),
]
