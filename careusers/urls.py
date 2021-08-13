from django.contrib.auth import views
from django.urls import path
from careusers.views import CareuserListView,CareuserEditView,CareuserCreateView
from django.contrib.auth.decorators import login_required

app_name = "careusers"

urlpatterns = [

    #以下はstaffuserのみアクセス可能(viewsにて制限)
    path("list/",login_required(CareuserListView.as_view()),name="list"),
    path("list/edit/<int:pk>/",login_required(CareuserEditView.as_view()),name="edit"),
    path("list/new/",login_required(CareuserCreateView.as_view()),name="new"),
]