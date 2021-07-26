# -*- coding: UTF-8 -*-
from collections import namedtuple
import datetime
from django.core.checks import messages
from django.db.models.fields import reverse_related
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls.conf import path
from . import models
from . import forms
from django.contrib.auth.hashers import check_password, make_password
from . import function
from django.utils import timezone

# Create your views here.
def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')

def login(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        passwd = request.POST.get('passwd')
        message = 'Wrong type.'
        if user_id.strip() and passwd:
            #if passwd has some restrict, write here
            try:
                user = models.User.objects.get(user_id=user_id)
            except:
                message = 'Wrong ID!'
                return render(request, 'login/login.html', {'message': message})
            if user.status != 0:
                message = '沒有資格'
                return render(request, 'login/login.html', {'message':message})
            if  check_password(passwd, user.passwd):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['is_boss'] = user.boss
                request.session['is_hr'] = user.hr
                request.session['is_manager'] = user.manager
                return redirect('/index/')
            else:
                message = 'Wrong passwd!'
                return render(request, 'login/login.html', {'message': message})
        else:
            return render(request, 'login/login.html', {'message': message})
    return render(request, 'login/login.html')

def set_admin(request):
    try:
        admin = models.User.objects.get(name="admin")
    except:
        admin = models.User()
        admin.name = "admin"
        admin.user_id = "admin"
        admin.passwd = make_password("admin")
        admin.email = "admin@gmail.com"
        admin.department = "superadmin"
        admin.salary = 1
        admin.hr = True
        admin.manager = True
        admin.save()
    return redirect("/login/")

def profile(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    user = models.User.objects.get(id=request.session['user_id'])
    annual = 0
    back = "/index/"
    return render(request, 'login/profile.html', locals())

def change_passwd(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    title = "修改密碼"
    back = "/index/"
    mode = "/change_passwd/"
    #get 
    if request.method == 'POST':
        user = models.User.objects.get(id=request.session['user_id'])
        passwd_form = forms.Passwd(request.POST)
        if passwd_form.is_valid():
            origin = passwd_form.cleaned_data.get('origin')
            if  check_password(origin, user.passwd):
                new = passwd_form.cleaned_data.get('new')
                password = make_password(new)
                user.passwd = password
                user.save()
                return redirect("/logout/")
            else:
                message = "原密碼錯誤"
                return render(request, 'login/change_passwd.html', locals())
    passwd_form = forms.Passwd()
    return render(request, 'login/change_passwd.html', locals())

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

def leave(request,id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if id!=0:
        leave = models.Leave.objects.get(id=id)
        if leave.checked:
            return redirect(f"/display_leave/{id}/")
        if leave.user_id.id != request.session['user_id']:
            return redirect("/leave_list/")
    else:
        leave = models.Leave()
    if request.method == 'POST':
        leave_form = forms.LeaveForm(request.POST)
        message = "please check the input type"
        if leave_form.is_valid():
            s = leave_form.cleaned_data.get('start')
            e = leave_form.cleaned_data.get('end')
            leave.year = leave_form.cleaned_data.get('year')
            leave.month = leave_form.cleaned_data.get('month')
            leave.start = s
            leave.end = e
            leave.category = leave_form.cleaned_data.get('category')
            leave.special = leave_form.cleaned_data.get('special')
            leave.checked = False
            #get total time
            if leave.month >12:
                message = "日期格式錯誤"
                return render(request, 'login/leave.html', locals())
            leave.total = function.get_day(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)                
            if leave.total < 0:
                message = "時間格式錯誤"
                return render(request, 'login/leave.html', locals())
            leave.total_time = leave.total*8
            #get user
            if id==0:
                leave.user_id = models.User.objects.get(id=request.session['user_id'])
            #insert
            leave.save()
            #redirect
            return redirect(f"/display_leave/{leave.id}")
        else:
            message ="格式錯誤"
            return render(request, 'login/leave.html', locals())
    if id==0:
        leave_form = forms.LeaveForm()
    else:
        leave_form = forms.LeaveForm(initial={'year':leave.year, 'month':leave.month, 'start':leave.start, 'end':leave.end,
                                                'category':leave.category, 'special':leave.special})
    return render(request, 'login/leave.html', locals())

def leave_list(request):
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
    checked = f"{year}/{mon}已核准假單"
    unchecked = f"{year}/{mon}未核准假單"
    checks = models.Leave.objects.filter(user_id=request.session['user_id'], month=mon, year=year, checked=True)
    n_checks = models.Leave.objects.filter(user_id=request.session['user_id'], month=mon, year=year, checked=False)
    apply = "請假申請"
    href = "/leave/"
    title = "leave"
    action = "/leave_list/"
    submit = "送出"
    return render(request, 'login/list.html', locals())

def show_leave(request, id):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    user = models.User.objects.get(id=request.session['user_id'])
    try:
        leave = models.Leave.objects.get(id=id)
    except:
        return redirect("/leave_list/")
    if request.session['user_id'] == leave.user_id.id or (request.session['is_manager'] and user.department == leave.user_id.department) or request.session['is_hr']:
        return render(request, "login/display_leave.html", locals())
    else:
        return redirect("/leave_list/")


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

def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    #delete session
    request.session.flush()
    #or below
    #del request.session['is_login']
    #del request.session['user_id']
    #del request.session['user_name']
    return redirect("/login/")


def hr_menu(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    return render(request, 'hr/hr_menu.html')

def hr_profile(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    users = models.User.objects.filter(status=0).exclude(name="admin")
    stops = models.User.objects.filter(status=2)
    return render(request, 'hr/hr_profile.html', locals())

def hr_profile_leave(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    resigns = models.User.objects.filter(status=1)
    return render(request, 'hr/hr_profile.html', locals())

def resign(request, id):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    user = models.User.objects.get(id=id)
    return render(request, 'hr/resign.html', locals())

def hr_personal(request, id):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    try:
        user = models.User.objects.get(id=id)
    except:
        return redirect("/hr/profile/")
    back = "/hr/profile/"
    return render(request, 'login/profile.html', locals())


def status(request, user, status):
    try:
        users = models.User.objects.get(id=user)
    except:
        return redirect("/hr/profile/")
    users.status = status
    if status == 1:
        users.resign = datetime.date.today()
    users.save()
    return redirect(f"/hr/profile/{user}")

def hr_edit(request, id):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    func = "edit"
    title = "修改資料"
    action = f"/hr/edit/{id}/"
    user = models.User.objects.get(id=id)
    register_form = forms.SignUp(initial={'name':user.name, 'email':user.email, 'user_id':user.user_id,
                        'passwd':user.passwd, 'department':user.department,
                        'on_job':user.on_job, 'salary':user.salary, 'boss':user.boss, 'hr':user.hr,
                        'manager':user.manager, 'staff':user.staff, 'self_percent':user.self_percent,})
    back = f"/hr/profile/{user.id}/"
    if request.method == 'POST':
        register_form = forms.SignUp(request.POST)
        if register_form.is_valid():
            user = models.User.objects.get(id=id)
            user.name = register_form.cleaned_data.get('name')
            user.email = register_form.cleaned_data.get('email')
            user.department = register_form.cleaned_data.get('department')
            user.on_job = register_form.cleaned_data.get('on_job')
            user.salary = register_form.cleaned_data.get('salary')
            user.boss = register_form.cleaned_data.get('boss')
            user.hr = register_form.cleaned_data.get('hr')
            user.manager = register_form.cleaned_data.get('manager')
            user.staff = register_form.cleaned_data.get('staff')
            user.self_percent= register_form.cleaned_data.get('self_percent')
            #get level
            user.labor = function.find_labor(user.salary)
            user.health = function.find_health(user.salary)
            user.retirement = function.find_retirement(user.salary)
            #retire self
            if user.self_percent <= 6:
                pass
            else:
                message = "自提撥最高是6％"
                return render(request, 'hr/register.html', locals())
            user.retire_self = function.retire_M(user.retirement)*user.self_percent/100
            user.seniority = function.get_seniority(user.on_job.year, user.on_job.month, user.on_job.day)
            user.annual = function.get_annual(user.seniority)
            user.save()
            return redirect(f'/hr/profile/{user.id}/')
    return render(request, 'hr/register.html', locals())

def hr_register(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if request.method == 'POST':
        register_form = forms.SignUp(request.POST)
        message = "please check input type."
        if register_form.is_valid():
            #insert
            new_User = models.User()
            new_User.name = register_form.cleaned_data.get('name')
            new_User.department = register_form.cleaned_data.get('department')
            new_User.salary = register_form.cleaned_data.get('salary')
            new_User.on_job = register_form.cleaned_data.get('on_job')
            new_User.boss = register_form.cleaned_data.get('boss')
            new_User.hr = register_form.cleaned_data.get('hr')
            new_User.manager = register_form.cleaned_data.get('manager')
            new_User.staff = register_form.cleaned_data.get('staff')
            new_User.self_percent = register_form.cleaned_data.get('self_percent')
            user_id = register_form.cleaned_data.get('user_id')
            passwd = register_form.cleaned_data.get('passwd')
            email = register_form.cleaned_data.get('email')
            #hash passwd
            password = make_password(passwd)
            #check validate
            same_id = models.User.objects.filter(user_id=user_id)
            if same_id:
                message = 'Same user ID.'
                return render(request, 'hr/register.html', locals())
            same_email = models.User.objects.filter(email=email)
            if same_email:
                message = 'Same E-mail.'
                return render(request, 'hr/register.html', locals())
            #insert
            new_User.user_id = user_id
            new_User.passwd = password
            new_User.email = email
            #get level
            new_User.labor = function.find_labor(new_User.salary)
            new_User.health = function.find_health(new_User.salary)
            new_User.retirement = function.find_retirement(new_User.salary)
                        #retire self
            if new_User.self_percent <= 6:
                pass
            else:
                message = "自提撥最高是6％"
                return render(request, 'hr/register.html', locals())
            new_User.retire_self = function.retire_M(new_User.retirement)*new_User.self_percent/100
            new_User.seniority = function.get_seniority(new_User.on_job.year, new_User.on_job.month, new_User.on_job.day)
            new_User.annual = function.get_annual(new_User.seniority)
            new_User.save()
            #redirect
            return redirect('/hr/menu/')
        else:
            return render(request, 'hr/register.html', locals())
    register_form = forms.SignUp()
    back = "/hr/menu/"
    action = "/hr/register/"
    title = "建立員工資料"
    return render(request, 'hr/register.html', locals()) 


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

def hr_leave(request, id=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if id == 0:
        mode = "user"
        objects = models.User.objects.filter(status=0).exclude(name="admin")
        stops = models.User.objects.filter(status=2)
        title = "請選擇員工"
        href = "/hr/leave"
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
        action = f"/hr/leave/{id}/"
        submit = "送出"
        mode = "leave"
        user = models.User.objects.get(id=id)
        objects = models.Leave.objects.filter(user_id=id, month=mon, year=year, checked=True)
        title = f"{year}/{mon} {user.name}的已核准假單"
        href = "/display_leave"
        back = "/hr/leave/"
        return render(request, 'hr/list.html', locals())

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


def hr_salary(request): 
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if not request.session.get('is_salary', None):
        return redirect("/hr/salary_pass/")
    if request.method == "POST":
        month_form = forms.MonthForm(request.POST)
        if month_form.is_valid():
            year = month_form.cleaned_data.get('year')
            month = month_form.cleaned_data.get('month')
            Users = models.User.objects.filter(status=0).exclude(name="admin")
            for user in Users:
                try:
                    total = models.Total.objects.get(user_id__id=user.id, month=month, year=year)
                    total_leave = models.Total_leave.objects.get(id=total.total_leave.id)
                    total.reset()
                    total_leave.reset()
                except:
                    total = models.Total()
                    total.year = year
                    total.month = month
                    total_leave = models.Total_leave()
                    total.user_id = user
                #overtime
                Overtimes = models.Overtime.objects.filter(user_id__id=user.id, month=month, year=year, checked=True)
                day_rate = float(user.salary)/float(30)
                hour_rate = float(user.salary)/float(30*8)
                minute_rate = float(hour_rate)/float(60)
                all_time = 0
                flag = 0
                for overtime in Overtimes:
                    try:
                        day = models.Calender.objects.get(day=datetime.date(overtime.year,overtime.month,overtime.day))
                    except:
                        day = models.Calender()
                        day.sort = "五"
                    if day.sort == "六":
                        total.over_613 += overtime.one_third
                        total.over_623 += overtime.two_third
                        total.over_223 += overtime.double
                        total.free_over += overtime.one_third + overtime.two_third + overtime.double
                        total.free_over_add += overtime.one_third*(minute_rate*4/3) + overtime.two_third*(minute_rate*5/3) + overtime.double*(minute_rate*8/3)
                    elif day.sort == "日":
                        total.over_2 += overtime.double
                        total.free_over += overtime.double
                        total.free_over_add += overtime.double*(minute_rate*2)
                    else:
                        if flag:
                            total.tax_over += overtime.one_third
                            total.over_13 += overtime.one_third
                            total.tax_over_add += overtime.one_third*(minute_rate*4/3)
                        else:
                            total.over_13 += overtime.one_third
                            all_time += overtime.one_third
                            if all_time == 46*60:
                                flag = 1
                            elif all_time > 46*60:
                                flag = 1
                                tax = all_time - 46*60
                                total.tax_over += tax
                                total.free_over += overtime.one_third - tax
                                total.tax_over_add += tax*(minute_rate*4/3)
                                total.free_over_add += (overtime.one_third - tax)*(minute_rate*4/3)
                            else:
                                total.free_over += overtime.one_third
                                total.free_over_add += overtime.one_third*(minute_rate*4/3)
                        if flag:
                            total.tax_over += overtime.two_third
                            total.over_23 += overtime.two_third
                            total.tax_over_add += overtime.two_third*(minute_rate*5/3)
                        else:
                            total.over_23 += overtime.two_third
                            all_time += overtime.two_third
                            if all_time == 46*60:
                                flag = 1
                            elif all_time > 46*60:
                                flag = 1
                                tax = all_time - 46*60
                                total.tax_over += tax
                                total.free_over += overtime.two_third - tax
                                total.tax_over_add += tax*(minute_rate*5/3)
                                total.free_over_add += (overtime.two_third - tax)*(minute_rate*5/3)
                            else:
                                total.free_over += overtime.two_third
                                total.free_over_add += overtime.two_third*(minute_rate*5/3)
                    total.tax_over_add = round(total.tax_over_add,2)
                    total.free_over_add = round(total.free_over_add,2)
                #leave
                Leaves = models.Leave.objects.filter(user_id__id=user.id, month=month, year=year, checked=True)
                for leave in Leaves:
                    if leave.category == "病假":
                        total_leave.sick += leave.total_time
                        total_leave.sick_deduce += leave.total_time*hour_rate*0.5
                    elif leave.category == "生理假":
                        total_leave.menstrual += leave.total_time
                        total_leave.menstrual_deduce += leave.total_time*hour_rate*0.5
                    elif leave.category == "事假":
                        total_leave.personal += leave.total_time
                        total_leave.personal_deduce += leave.total_time*hour_rate
                    elif leave.category == "家庭照顧假":
                        total_leave.takecare += leave.total_time
                        total_leave.care_deduce += leave.total_time*hour_rate
                    elif leave.category == "育嬰假":
                        total_leave.nursery += leave.total
                        total_leave.nursery_deduce += leave.total*day_rate
                    elif leave.category == "無薪假":
                        total_leave.unpaid += leave.total
                        total_leave.unpaid_deduce += leave.total*day_rate
                    elif leave.category == "防疫隔離假":
                        total_leave.other1 += leave.total
                        total_leave.other1_deduce += leave.total*day_rate
                    elif leave.category == "防疫照顧假":
                        total_leave.other2 += leave.total_time
                        total_leave.other2_deduce += leave.total_time*hour_rate
                    elif leave.category == "疫苗接種假":
                        total_leave.other3 += leave.total_time
                        total_leave.other3_deduce += leave.total_time*hour_rate
                    elif leave.category == "因公隔離":
                        total_leave.other4 += leave.total
                        total_leave.other4_deduce += leave.total*day_rate*0.5
                    elif leave.category == "出差":
                        total_leave.business += leave.total
                    elif leave.category == "公假":
                        total_leave.official += leave.total
                    elif leave.category == "工傷假":
                        total_leave.injury += leave.total
                    elif leave.category == "喪假":
                        total_leave.funeral += leave.total
                    elif leave.category == "婚假":
                        total_leave.marriage += leave.total
                    elif leave.category == "產假":
                        total_leave.maternity += leave.total
                    elif leave.category == "陪產假":
                        total_leave.paternity == leave.total
                    elif leave.category == "產前假":
                        total_leave.prenatal += leave.total
                    elif leave.category == "特休":
                        total_leave.annual += leave.total
                    elif leave.category == "補休":
                        total_leave.rest += leave.total
                    else:
                        pass
                total_leave.save()
                total.total_leave = total_leave
                user.annual_used += total_leave.annual
                #late
                Dailys = models.Daily.objects.filter(user_id__id=user.id, month=month, year=year, check=True)
                for daily in Dailys:
                    total.leave_early += daily.leave_early_fixed
                decrease = total_leave.care_deduce + total_leave.sick_deduce +total_leave.other1_deduce + total_leave.other2_deduce + total_leave.other3_deduce + total_leave.other4_deduce + total_leave.unpaid_deduce + total_leave.nursery_deduce + total_leave.personal_deduce + total_leave.menstrual_deduce
                decrease += total.leave_early * minute_rate + user.retire_self
                total.tax = user.salary - decrease + total.tax_over_add
                decrease += function.convert_labor(user.labor) + function.convert_health(user.health) 
                total.decrease = decrease
                total.actual_salary = user.salary - total.decrease + total.tax_over_add + total.free_over_add
                total.save()
            message = "計算成功"
            return render(request, "hr/hr_menu.html", locals())
    else:
        month_form = forms.MonthForm()
        action = "/hr/salary/"
        mode = "user"
        objects = models.User.objects.filter(status=0).exclude(name="admin")
        stops = models.User.objects.filter(status=2)
        href = "/hr/list_total"
        back = "/hr/menu/"
        title = "請選擇員工"
        submit = "計算"
        return render(request, "hr/salary.html", locals())

def list_total(request, userid=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if not request.session.get('is_salary', None):
        return redirect("/hr/salary_pass/")
    try:
        user = models.User.objects.get(id=userid)
    except:
        return redirect("/hr/salary/")
    objects = models.Total.objects.filter(user_id__id=userid)
    mode = "total"
    href = f"/hr/show_total"
    back = "/hr/salary/"
    title = f"{user.name}的薪資總表"
    return render(request, "hr/salary.html", locals())

def show_total(request, totalid=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if not request.session.get('is_salary', None):
        return redirect("/hr/salary_pass/")
    try:
        total = models.Total.objects.get(id=totalid)
    except:
        return redirect("/hr/salary/")
    labor = function.convert_labor(total.user_id.labor)
    health = function.convert_health(total.user_id.health)
    retire = function.convert_retirement(total.user_id.retirement)
    tax_over = round(total.tax_over/60,2)
    free_over = round(total.free_over/60,2)
    return render(request, "hr/display_total.html", locals())

def salary_pass(request):
    try:
        admin_user = models.User.objects.get(name="admin")
    except:
        return redirect("/hr/menu/")
    message = ""
    if request.session.get('is_salary', None):
        return redirect("/hr/menu/")
    if request.method == "POST":
        password = request.POST.get('passwd')
        if check_password(password, admin_user.passwd):
            request.session['is_salary'] = True
            return redirect("/hr/menu/")
        else:
            message = "Wrong password"
    return render(request, 'hr/salary_pass.html', {'message': message})

def hr_passwd(request):
    try:
        admin = models.User.objects.get(name="admin")
    except:
        return redirect("/hr/menu/")
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    title = "修改薪資密碼"
    action = "/hr/change_passwd/"
    back = "/hr/menu"
    #get 
    if request.method == 'POST':
        #change to admin passwd
        hr_passwd = forms.Passwd(request.POST)
        if hr_passwd.is_valid():
            origin = hr_passwd.cleaned_data.get('origin')
            if  check_password(origin, admin.passwd):
                new = hr_passwd.cleaned_data.get('new')
                password = make_password(new)
                admin.passwd = password
                admin.save()
                del request.session['is_salary']
                return redirect("/hr/menu/")
            else:
                message = "原密碼錯誤"
                passwd_form = forms.Passwd()
                return render(request, 'login/change_passwd.html', locals())
    passwd_form = forms.Passwd()
    return render(request, 'login/change_passwd.html', locals())

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

def day_off(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    day_form = forms.DayForm()
    if request.method == "POST":
        day_form = forms.DayForm(request.POST)
        if day_form.is_valid():
            day = day_form.cleaned_data.get('day')
            sort = day_form.cleaned_data.get('sort')
            try:
                day_off = models.Calender.objects.get(day=day)
            except:
                day_off = models.Calender()
            day_off.day = day
            day_off.sort = sort
            day_off.save()
        else:
            message = "Wrong type"
    offs = models.Calender.objects.all()
    return render(request, "hr/day_off.html", locals())

def delete_off(request,id):
    if not request.session.get('is_hr',None):
        return redirect("/index/")
    try:
        day_off = models.Calender.objects.get(id=id)
        day_off.delete()
    except:
        pass
    return redirect("/hr/set_day_off/")