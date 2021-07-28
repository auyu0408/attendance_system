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
    path('', views.user.index),
    path('index/', views.user.index),
    path('login/', views.user.login),
    path('set_admin/', views.user.set_admin),
    path('profile/', views.user.profile),
    path('change_passwd/', views.user.change_passwd),

    path('attendance/', views.attend.attendance),
    path('attendance/<int:id>/', views.attend.daily),

    path('daily/', views.attend.daily),
    path('daily/<int:id>/', views.attend.daily),

    path('leave_list/', views.leave.leave_list),
    path('leave/', views.leave.leave),
    path('leave/<int:id>/', views.leave.leave),
    path('display_leave/<int:id>/', views.leave.show_leave),
    path('delete_leave/<int:id>/', views.leave.delete_leave),

    path('overtime_list/', views.overtime.overtime_list),
    path('overtime/', views.overtime.overtime),
    path('overtime/<int:id>/', views.overtime.overtime),
    path('display_overtime/<int:id>/', views.overtime.show_overtime),

    path('check_list/', views.check.check_list),
    path('check/', views.check.check),

    path('logout/', views.user.logout),
    path('hr/', include([
        path('menu/', views.hr.hr_menu),
        path('profile/', views.hr.hr_profile),
        path('profile/<int:id>/', views.hr.hr_personal),

        path('profile_leave/', views.hr.hr_profile_leave),
        path('profile_leave/<int:id>/', views.hr.resign),
        path('status/<int:user>/<int:status>/', views.hr.status),

        path('edit/<int:id>/', views.hr.hr_edit),
        path('register/', views.hr.hr_register),
        path('attendance/', views.attend.hr_attendance),
        path('attendance/<int:id>/', views.attend.hr_attendance),

        path('leave/', views.leave.hr_leave),
        path('leave/<int:id>/', views.leave.hr_leave),

        path('overtime/', views.overtime.hr_overtime),
        path('overtime/<int:id>/', views.overtime.hr_overtime),
        path('checked/',views.check.hr_checked),

        path('salary/', views.total.hr_salary),
        path('list_total/<int:userid>/',views.total.list_total),
        path('show_total/<int:totalid>/',views.total.show_total),
        path('salary_pass/', views.user.salary_pass),
        path('change_passwd/', views.user.hr_passwd),

        path('set_day_off/', views.calender.day_off),
        path('delete_off/<int:id>/', views.calender.delete_off),
    ])),

    path('check_in_out/', views.attend.check_in_out),
]
