from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = "services"

urlpatterns = [

    #以下はsuperuserのみアクセス可能(viewsにて制限)
    path("list/",login_required(views.ServiceListView.as_view()),name="list"),
    path("list/edit/<int:pk>/",login_required(views.ServiceEditView.as_view()),name="edit"),
    path("list/new/",login_required(views.ServiceCreateView.as_view()),name="new"),
]