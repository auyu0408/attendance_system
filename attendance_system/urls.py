"""attendance_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.urls.conf import include
from attendance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('login/', views.login),
    path('profile/', views.profile),
    path('change_passwd/', views.change_passwd),
    path('attendance/', views.attendance),
    path('leave/', views.leave),
    path('overtime/', views.overtime),
    path('check/', views.check),
    path('logout/', views.logout),
    path('hr/', include([
        path('menu/', views.hr_menu),
        path('profile/', views.hr_profile),
        path('register/', views.hr_register),
        path('attendance/', views.hr_attendance),
        path('leave/', views.hr_leave),
        path('salary/', views.hr_salary),
        path('bonus/', views.hr_bonus),
    ])),
]
