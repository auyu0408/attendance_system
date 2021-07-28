# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from attendance import function

def check_list(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if not request.session.get('is_manager', None) and not request.session.get('is_boss', None):
        return redirect("/index/")
    user = models.User.objects.get(id=request.session['user_id'])
    month_form = forms.MonthForm()
    year = datetime.datetime.today().year
    mon = datetime.datetime.today().month
    action = "/check_list/"
    submit = "送出"
    if request.method == "POST":
        month_form = forms.MonthForm(request.POST)
        if month_form.is_valid():
            year = month_form.cleaned_data.get('year')
            mon = month_form.cleaned_data.get('month')
    if user.boss:
        n_leaves = models.Leave.objects.filter(user_id__manager=True, checked=False, month=mon, year=year)
        leaves = models.Leave.objects.filter(user_id__manager=True, checked=True, month=mon, year=year)
        n_overtimes = models.Overtime.objects.filter(user_id__manager=True, checked=False, month=mon, year=year)
        overtimes = models.Overtime.objects.filter(user_id__manager=True, checked=True, month=mon, year=year)
    
    else:
        n_leaves = models.Leave.objects.filter(checked=False, user_id__department=user.department, month=mon, year=year).exclude(user_id=user.id)
        leaves = models.Leave.objects.filter(checked=True, user_id__department=user.department, month=mon, year=year).exclude(user_id=user.id)
        n_overtimes = models.Overtime.objects.filter(checked=False, user_id__department=user.department, month=mon, year=year).exclude(user_id=user.id)
        overtimes = models.Overtime.objects.filter(checked=True, user_id__department=user.department, month=mon, year=year).exclude(user_id=user.id)
    
    return render(request, 'login/check_list.html', locals())

def check(request):
    if request.method=="POST":
        id =request.POST['form_id']
        form_type = request.POST['form_type']
        if form_type == "leave":
            leave = models.Leave.objects.get(id=id)
            day = leave.end.day - leave.start.day
            if day == 0:
                try:
                    daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=leave.start.day, user_id=leave.user_id)
                except:
                    daily = models.Daily(year=leave.year, month=leave.month, day=leave.start.day, user_id=leave.user_id)
                daily.holiday = leave.total_time
                daily.holiday_reason = leave.category
                daily.check = False
                daily.save()
            else:
                try:
                    daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=leave.start.day, user_id=leave.user_id)
                except:
                    daily = models.Daily(year=leave.year, month=leave.month, day=leave.start.day, user_id=leave.user_id)
                daily.holiday = function.get_hour(leave.year, leave.month, leave.start.day, leave.start.hour, leave.start.minute, leave.year, leave.month, leave.start.day, 17, 0)
                daily.holiday_reason = leave.category
                daily.check = False
                daily.save()
                for date in range(leave.start.day+1, leave.end.day):
                    try:
                        calender_day = models.Calender.objects.get(day=datetime.date(leave.year,leave.month, date))
                    except:
                        calender_day = models.Calender()
                        calender_day.sort = "五"
                    if calender_day.sort != "五":
                        continue
                    try:
                        daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=date, user_id=leave.user_id)
                    except:
                        daily = models.Daily(year=leave.year, month=leave.month, day=date, user_id=leave.user_id)
                    daily.holiday = 8
                    daily.holiday_reason = leave.category
                    daily.check = False
                    daily.save()
                try:
                    daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=leave.end.day, user_id=leave.user_id)
                except:
                    daily = models.Daily(year=leave.year, month=leave.month, day=leave.end.day, user_id=leave.user_id)
                daily.holiday = function.get_hour(leave.year, leave.month, leave.end.day, 8, 0, leave.year, leave.month, leave.end.day, leave.end.hour, leave.end.minute)
                daily.check = False
                daily.save()
            leave.checked = True
            leave.save()
        else:
            overtime = models.Overtime.objects.get(id=id)
            overtime.checked = True
            day = overtime.day
            try:
                daily = models.Daily.objects.get(year=overtime.year, month=overtime.month, day=overtime.day, user_id=overtime.user_id)
            except:
                daily = models.Daily(year=overtime.year, month=overtime.month, day=overtime.day, user_id=overtime.user_id)
            daily.can_overtime = overtime.one_third + overtime.two_third + overtime.double
            daily.save()
            overtime.save()
    return redirect(f"/display_{form_type}/{id}/")

def hr_checked(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    month_form = forms.MonthForm()
    mon = datetime.date.today().month
    year = datetime.date.today().year
    if request.method == "POST":
        month_form = forms.MonthForm(request.POST)
        if month_form.is_valid():
            mon = month_form.cleaned_data.get('month')
            year = month_form.cleaned_data.get('year')
        dailys = models.Daily.objects.filter(year=year, month=mon, check=False)
        for daily in dailys:
            try:
                overtime = models.Overtime.objects.get(year=daily.year, month=daily.month, day=daily.day, user_id=daily.user_id)
            except:
                pass
            try:
                calender_day = models.Calender.objects.get(day=datetime.date(daily.year, daily.month, daily.day))
            except:
                calender_day = models.Calender
                calender_day.sort = "五"
            if calender_day.sort == "六":
                if daily.overtime_fixed == daily.can_overtime:
                    pass
                elif daily.overtime_fixed < daily.can_overtime:
                    if daily.overtime_fixed < 120:
                        overtime.one_third = daily.overtime_fixed
                        overtime.two_third = 0
                        overtime.double = 0
                    elif daily.overtime_fixed < 480:
                        overtime.one_third = 120
                        overtime.two_third = daily.overtime_fixed-120
                        overtime.double = 0
                    else:
                        overtime.one_third = 120
                        overtime.two_third = 360
                        overtime.double = daily.overtime_fixed - 480
                    daily.can_overtime = daily.overtime_fixed
                    overtime.save()
                else: continue
            elif calender_day.sort == "日":
                print(0)
                if daily.overtime_fixed == daily.can_overtime:
                    pass
                    print(1)
                elif daily.overtime_fixed < daily.can_overtime:
                    overtime.one_third = 0
                    overtime.two_third = 0
                    overtime.double = daily.overtime_fixed
                    daily.can_overtime = daily.overtime_fixed
                    overtime.save()
                else: continue
            else:
                if daily.holiday == 0:
                    if daily.attend_fixed + round(daily.leave_early_fixed/60,2) >= 8:
                        pass
                    else: continue
                else:
                    if daily.attend_fixed + daily.holiday >= 8:
                        daily.leave_early_fixed = 0
                    else:continue
                #overtime
                if daily.overtime_fixed == daily.can_overtime:
                    pass
                elif daily.overtime_fixed < daily.can_overtime:
                    if daily.overtime_fixed < 120:
                        overtime.one_third = daily.overtime_fixed
                        overtime.two_third = 0
                        overtime.double = 0
                    elif daily.overtime_fixed < 240:
                        overtime.one_third = 120
                        overtime.two_third = daily.overtime_fixed-120
                        overtime.double = 0
                    else: continue
                    daily.can_overtime = daily.overtime_fixed
                    overtime.save()
                else: continue
            daily.check = True
            daily.save()
    wrongs = models.Daily.objects.filter(check=False)
    action = "/hr/checked/"
    submit = "核對"
    return render(request, 'hr/daily_check.html', locals())