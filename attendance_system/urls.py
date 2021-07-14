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

    path('leave_list/', views.leave_list),
    path('leave/', views.leave),
    path('leave/<int:id>/', views.leave),
    path('display_leave/<int:id>/', views.show_leave),

    path('overtime_list/', views.overtime_list),
    path('overtime/', views.overtime),
    path('overtime/<int:id>/', views.overtime),
    path('display_overtime/<int:id>/', views.show_overtime),

    path('check_list/', views.check_list),
    path('check/', views.check),

    path('logout/', views.logout),
    path('hr/', include([
        path('menu/', views.hr_menu),
        path('profile/', views.hr_profile),
        path('profile/<int:id>/', views.hr_personal),

        path('edit/<int:id>/', views.hr_edit),
        path('register/', views.hr_register),
        path('attendance/', views.hr_attendance),

        path('leave/', views.hr_leave),
        path('leave/<int:id>/', views.hr_leave),

        path('overtime/', views.hr_overtime),
        path('overtime/<int:id>/', views.hr_overtime),

        path('salary/', views.hr_salary),
        path('salary_pass/', views.salary_pass),
        path('change_passwd/', views.hr_passwd),
        path('bonus/', views.hr_bonus),
    ])),

    path('check_in_out/', views.check_in_out),
]
