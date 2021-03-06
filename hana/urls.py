"""hana URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from django.http import HttpResponse


urlpatterns = [
    #staffs.admin.pyのadmin.site.register(User, MyUserAdmin)もコメントアウト済み
    #path("ad_ksg/", admin.site.urls),
    path("staff/",include("staffs.urls")), 
    path("careuser/",include("careusers.urls")),
    path("service/",include("services.urls")),
    path("schedule/",include("schedules.urls")),
    path("aggregate/",include("aggregates.urls")),
    path("pdf/",include("pdfgen.urls")),
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
]