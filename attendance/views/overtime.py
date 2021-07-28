# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from attendance import function

def overtime(request, id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if id!=0:
        overtime = models.Overtime.objects.get(id=id)
        if overtime.checked:
            return redirect(f"/display_overtime/{id}")
        if overtime.user_id.id != request.session['user_id']:
            return redirect(f"/overtime_list/")
    else:
        overtime = models.Overtime()
    if request.method == 'POST':
        overtime_form = forms.OvertimeForm(request.POST)
        message = "please check the input type"
        if overtime_form.is_valid():
            overtime.year = overtime_form.cleaned_data.get('year')
            overtime.month = overtime_form.cleaned_data.get('month')
            overtime.day = overtime_form.cleaned_data.get('day')
            s = overtime_form.cleaned_data.get('start')
            e = overtime_form.cleaned_data.get('end')
            overtime.start = s
            overtime.end = e
            overtime.reason = overtime_form.cleaned_data.get('reason')
            # get time
            try:
                date = datetime.date(overtime.year, overtime.month, overtime.day)
            except:
                message = "日期格式錯誤"
                return render(request, 'login/overtime.html', locals())
            try:
                calender_day = models.Calender.objects.get(day=date)
            except:
                calender_day = models.Calender()
                calender_day.sort = "五"
            if calender_day.sort == "日":
                overtime.double = function.get_minute(overtime.year, overtime.month, overtime.day, s.hour, s.minute, overtime.year, overtime.month, overtime.day, e.hour, e.minute)
                overtime.one_third = 0
                overtime.two_third = 0
            else:
                total_minute = function.get_minute(overtime.year, overtime.month, overtime.day, s.hour, s.minute, overtime.year, overtime.month, overtime.day, e.hour, e.minute)
                if total_minute < 120:
                    overtime.one_third = total_minute
                    overtime.two_third = 0
                    overtime.double = 0
                elif total_minute < 480:
                    overtime.one_third = 120
                    overtime.two_third = total_minute-120
                    overtime.double = 0
                else:
                    if calender_day.sort != "六":
                        message = "超過平日加班時間"
                    overtime.one_third = 120
                    overtime.two_third = 360
                    overtime.double = total_minute - 480
            #get user
            if id==0:
                overtime.user_id = models.User.objects.get(id=request.session['user_id'])
            #insert
            overtime.checked = False
            overtime.save()
            #redirect
            return redirect(f"/display_overtime/{overtime.id}/")
        else:
            return render(request, 'login/index.html', locals())
    if id==0:
        overtime_form = forms.OvertimeForm()
    else:
        overtime_form = forms.OvertimeForm(initial={ 'year':overtime.year, 'month':overtime.month, 'day':overtime.day, 'start':overtime.start, 'end':overtime.end,
                                                'reason':overtime.reason,})
    return render(request, 'login/overtime.html', locals())

def overtime_list(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    month_form = forms.MonthForm()
    year = datetime.datetime.today().year
    mon = datetime.datetime.today().month
    if request.method == "POST":
        month_form = forms.MonthForm(request.POST)
        if month_form.is_valid():
            year = month_form.cleaned_data.get('year')
            mon = month_form.cleaned_data.get('month')
    checked = f"{year}/{mon}已核准加班單"
    unchecked = f"{year}/{mon}未核准加班單"
    checks = models.Overtime.objects.filter(user_id=request.session['user_id'], month=mon, year=year, checked=True)
    n_checks = models.Overtime.objects.filter(user_id=request.session['user_id'], month=mon, year=year, checked=False)
    apply = "加班申請"
    href = "/overtime/"
    title = "overtime"
    submit = "送出"
    return render(request, 'login/list.html', locals())

def show_overtime(request, id):
    user = models.User.objects.get(id=request.session['user_id'])
    try:
        overtime = models.Overtime.objects.get(id=id)
        try:
            daily = models.Daily.objects.get(year=overtime.year, month=overtime.month, day=overtime.day, user_id=overtime.user_id)
        except:
            pass
    except:
        return redirect("/overtime_list/")
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if request.session['user_id'] == overtime.user_id.id or (request.session['is_manager'] and user.department == overtime.user_id.department) or request.session['is_hr']:
        return render(request, "login/display_overtime.html", locals())
    else:
        return redirect("/overtime_list/")

def hr_overtime(request, id=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if id == 0:
        mode = "user"
        objects = models.User.objects.filter(status=0).exclude(name="admin")
        stops = models.User.objects.filter(status=2)
        title = "請選擇員工"
        href = "/hr/overtime"
        back = "/hr/menu/"
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
        action = f"/hr/overtime/{id}/"
        submit = "送出"
        mode = "overtime"
        user = models.User.objects.get(id=id)
        objects = models.Overtime.objects.filter(user_id=id, checked=True, month=mon, year=year)
        title = f"{year}/{mon} {user.name}的已核准加班單"
        href = "/display_overtime"
        back = "/hr/overtime/"
        return render(request, 'hr/list.html', locals())
