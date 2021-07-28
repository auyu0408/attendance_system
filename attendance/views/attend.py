# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from attendance import function
from django.utils import timezone

def attendance(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    month_form = forms.MonthForm()
    year = datetime.datetime.today().year
    mon = datetime.datetime.today().month
    if request.method == "POST":
        month_form = forms.MonthForm(request.POST)
        if month_form.is_valid():
            mon = month_form.cleaned_data.get('month')
            year = month_form.cleaned_data.get('year')
    dailys = models.Daily.objects.filter(user_id=request.session['user_id'], month=mon, year=year)
    back = "/index/"
    action = "/attendance/"
    submit = "送出"
    title = f"{year}/{mon}出勤管理"
    return render(request, 'login/attendance.html', locals())

def daily(request, id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if request.method == 'POST':
        daily_form = forms.DailyForm(request.POST)
        if daily_form.is_valid():
            year = daily_form.cleaned_data.get('year')
            month = daily_form.cleaned_data.get('month')
            day = daily_form.cleaned_data.get('day')
            user_name = daily_form.cleaned_data.get('name')
            try:
                user = models.User.objects.get(name=user_name)
                if user.id == request.session['user_id'] or request.session['is_hr']:
                    pass
                else:
                    message = "請勿動他人資料"
                    return render(request, "hr/edit_daily.html", locals())
            except:
                message = "Wrong Name!"
                return render(request, "hr/edit_daily.html", locals())
            try:
                daily = models.Daily.objects.get(year=year, month=month, day=day, user_id=user)
            except:
                daily = models.Daily()
            daily.on_time_fixed = daily_form.cleaned_data.get('on_time_fixed')
            daily.off_time_fixed = daily_form.cleaned_data.get('off_time_fixed')
            daily.fixed_note = daily_form.cleaned_data.get('fixed_note')
            daily.year = year
            daily.month = month
            daily.day = day
            daily.user_id = user
            #get time
            on = daily.on_time_fixed
            off = daily.off_time_fixed
            daily.attend_fixed = function.get_attend(on.hour, on.minute, off.hour, off.minute)
            if datetime.date(daily.year, daily.month, daily.day).isoweekday() == 6 or datetime.date(daily.year, daily.month, daily.day).isoweekday() == 7:
                daily.attend_fixed = 0
                daily.overtime_fixed = function.get_minute(daily.year,daily.month,daily.day,on.hour,on.minute,daily.year,daily.month,daily.day,off.hour,off.minute)
            elif off.hour >= 17:
                if on.hour >= 17:
                    daily.overtime_fixed = function.get_minute(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
                else:
                    daily.overtime_fixed = function.get_minute(daily.year, daily.month, daily.day, 17, 0, daily.year, daily.month, daily.day, off.hour, off.minute)
            else:
                daily.overtime_fixed = 0
            #leave_early
            if datetime.date(daily.year, daily.month, daily.day).isoweekday() == 6 or datetime.date(daily.year, daily.month, daily.day).isoweekday() == 7:
                daily.leave_early_fixed = 0
            elif on.hour >= 8 and on.hour < 17:
                daily.leave_early_fixed = function.get_minute(daily.year, daily.month, daily.day, 8, 0, daily.year, daily.month, daily.day, on.hour, on.minute)
            else:
                daily.leave_early_fixed = 0
            if datetime.date(daily.year, daily.month, daily.day).isoweekday() == 6 or datetime.date(daily.year, daily.month, daily.day).isoweekday() == 7:
                daily.leave_early_fixed += 0
            elif off.hour < 17 and off.hour >= 8:
                daily.leave_early_fixed = daily.leave_early_fixed + function.get_minute(daily.year, daily.month, daily.day, off.hour, off.minute, daily.year, daily.month, daily.day, 17, 0)
            else:
                pass
            daily.save()
            message = "登記成功"
            return render(request, "login/index.html", locals())
        else:
            message = "Wrong type."
            return render(request, "hr/edit_daily.html", locals())
    else:
        if id!=0:
            daily = models.Daily.objects.get(id=id)
            daily_form = forms.DailyForm(initial={'name':daily.user_id.name, 'on_time_fixed':daily.on_time_fixed, 'off_time_fixed':daily.off_time_fixed,
                                        'year':daily.year, 'month':daily.month, 'day':daily.day,'fixed_note':daily.fixed_note,})
        else:
            daily_form = forms.DailyForm()
        return render(request, "hr/edit_daily.html", locals())

def hr_attendance(request, id=0):
    if not request.session.get('is_hr', None):
        return redirect("/attendance/")
    if id==0:
        mode = "user"
        title = "請選擇員工"
        href = "/hr/attendance"
        back = "/hr/menu/"
        objects = models.User.objects.filter(status=0).exclude(name="admin")
        stops = models.User.objects.filter(status=2)
        return render(request, 'hr/list.html', locals())
    else:
        month_form = forms.MonthForm()
        year = datetime.datetime.today().year
        mon = datetime.datetime.today().month
        if request.method == "POST":
            month_form = forms.MonthForm(request.POST)
            if month_form.is_valid():
                year = month_form.cleaned_data.get('year')
                mon = month_form.cleaned_data.get('month')
        user = models.User.objects.get(id=id)
        dailys = models.Daily.objects.filter(user_id__id=id, month=mon, year=year)
        back = "/hr/attendance/"
        action = f"/hr/attendance/{id}/"
        submit = "送出"
        title = f"{year}/{mon} {user.name}出勤"
        return render(request, 'login/attendance.html', locals())

def check_in_out(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    message = ""
    if request.method == "POST":
        now = timezone.now()
        user_id = request.POST.get('user_id')
        try:
            user = models.User.objects.get(user_id=user_id, status=0)
        except:
            message = "Wrong ID."
            return render(request, 'hr/check_in_out.html', {'message': message})
        try:
            daily = models.Daily.objects.get(user_id=user, day=now.day, month=now.month, year=now.year)
        except:
            daily = models.Daily()
            daily.on_time = now
            daily.on_time_fixed = now
        daily.user_id = user
        daily.year = datetime.date.today().year
        daily.month = datetime.date.today().month
        daily.day = datetime.date.today().day
        daily.off_time = now
        daily.off_time_fixed = now
        daily.halfway = 0
        daily.fixed_note=""
        #get time
        on = daily.on_time
        off = daily.off_time
        daily.attend = function.get_attend(on.hour, on.minute, off.hour, off.minute)
        if datetime.date(daily.year, daily.month, daily.day).isoweekday() == 6 and datetime.date(daily.year,daily.month,daily.day).isoweekday() == 7:
            datetime.attend = 0
            datetime.overtime = function.get_minute(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
        if off.hour >= 17:
            if on.hour >= 17:
                daily.overtime = function.get_minute(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
            else:
                daily.overtime = function.get_minute(daily.year, daily.month, daily.day, 17, 0, daily.year, daily.month, daily.day, off.hour, off.minute)
        else:
            daily.overtime = 0
        #leave_early
        if datetime.date(daily.year, daily.month, daily.day).isoweekday == 6 or datetime.date(daily.year, daily.month, daily.day) == 7:
            daily.leave_early = 0
        elif on.hour >= 8 and on.hour < 17:
            daily.leave_early = function.get_minute(daily.year, daily.month, daily.day, 8, 0, daily.year, daily.month, daily.day, on.hour, on.minute)
        else:
            daily.leave_early = 0
        if datetime.date(daily.year, daily.month, daily.day).isoweekday == 6 or datetime.date(daily.year, daily.month, daily.day) == 7:
            daily.leave_early += 0
        elif off.hour < 17 and off.hour >=8:
            daily.leave_early += function.get_minute(daily.year, daily.month, daily.day, off.hour, off.minute, daily.year, daily.month, daily.day, 17, 0)
        else:
            pass
        daily.attend_fixed = daily.attend
        daily.overtime_fixed = daily.overtime
        daily.leave_early_fixed = daily.leave_early
        daily.save()
        #else:
        #    daily.off_time = now
        #    daily.save()
        message = f"{user.name}簽到成功"
    return render(request, 'hr/check_in_out.html', {'message': message})