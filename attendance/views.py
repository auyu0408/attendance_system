# -*- coding: UTF-8 -*-
import datetime
from django.core.checks import messages
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
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
    dailys = models.Daily.objects.filter(user_id=request.session['user_id'])
    back = "/index/"
    return render(request, 'login/attendance.html', locals())

def daily(request, id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if id!=0:
        daily = models.Daily.objects.get(id=id)
    else:
        daily = models.Daily()
    if request.method == 'POST':
        daily_form = forms.DailyForm(request.POST)
        if daily_form.is_valid():
            daily.on_time = daily_form.cleaned_data.get('on_time')
            daily.off_time = daily_form.cleaned_data.get('off_time')
            daily.on_time_fixed = daily_form.cleaned_data.get('on_time_fixed')
            daily.off_time_fixed = daily_form.cleaned_data.get('off_time_fixed')
            daily.fixed_note = daily_form.cleaned_data.get('fixed_note')
            daily.year = daily_form.cleaned_data.get('year')
            daily.month = daily_form.cleaned_data.get('month')
            daily.day = daily_form.cleaned_data.get('day')
            user_name = daily_form.cleaned_data.get('name')
            try:
                user = models.User.objects.get(name=user_name)
            except:
                message = "Wrong Name!"
                return render(request, "hr/edit_daily.html", locals())
            user_id = user
            #get time
            on = daily.on_time
            off = daily.off_time
            daily.attend = function.get_hour(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
            if off.hour >= 17:
                daily.overtime = function.get_minute(daily.year, daily.month, daily.day, 17, 0, daily.year, daily.month, daily.day, off.hour, off.minute)
            else:
                daily.overtime = 0
            if on.hour >= 8:
                daily.leave_early = function.get_minute(daily.year, daily.month, daily.day, 8, 0, daily.year, daily.month, daily.day, on.hour, on.minute)
            else:
                daily.leave_early = 0
            if off.hour < 17:
                daily.leave_early = daily.leave_early + function.get_minute(daily.year, daily.month, daily.day, off.hour, off.minute, daily.year, daily.month, daily.day, 17, 0)
            else:
                daily.leave_early = daily.leave_early
            on = daily.on_time_fixed
            off = daily.off_time_fixed
            daily.attend_fixed = function.get_hour(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
            if off.hour >= 17:
                daily.overtime_fixed = function.get_minute(daily.year, daily.month, daily.day, 17, 0, daily.year, daily.month, daily.day, off.hour, off.minute)
            else:
                daily.overtime_fixed = 0
            if on.hour >= 8:
                daily.leave_early_fixed = function.get_minute(daily.year, daily.month, daily.day, 8, 0, daily.year, daily.month, daily.day, on.hour, on.minute)
            else:
                daily.leave_early_fixed = 0
            if off.hour < 17:
                daily.leave_early_fixed = daily.leave_early_fixed + function.get_minute(daily.year, daily.month, daily.day, off.hour, off.minute, daily.year, daily.month, daily.day, 17, 0)
            else:
                daily.leave_early_fixed = daily.leave_early_fixed
            daily.save()
            message = "修改成功"
            return render(request, "login/index.html", {'message':message})
        else:
            message = "Wrong type."
            return render(request, "hr/edit_daily.html", locals())
    else:
        if id!=0:
            daily_form = forms.DailyForm(initial={'name':daily.user_id.name, 'on_time':daily.on_time, 'off_time':daily.off_time,
                                        'on_time_fixed':daily.on_time_fixed, 'off_time_fixed':daily.off_time_fixed,
                                        'year':daily.year, 'month':daily.month, 'day':daily.day,'fixed_note':daily.fixed_note,})
            return render(request, "hr/edit_daily.html", locals())
        else:
            daily_form = forms.DailyForm()
            return render(request, "hr/edit_daily.html", locals())

def leave(request,id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if id!=0:
        leave = models.Leave.objects.get(id=id)
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
            leave.other_reason = leave_form.cleaned_data.get('other_reason')
            leave.special = leave_form.cleaned_data.get('special')
            leave.checked = False
            if leave.other_reason != "因公隔離" and leave.other_reason != "防疫照顧假" and leave.other_reason != "防疫隔離假" and leave.other_reason != "疫苗給薪假" and leave.other_reason != "":
                message = "Wrong reason type."
                
                return render(request, 'login/leave.html', locals())
            #get total time
            leave.total_time = function.get_hour(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)
            if leave.total_time - int(leave.total_time) > 0.5:
                leave.total_time = int(leave.total_time) + 1
            elif leave.total_time - int(leave.total_time) == 0:
                pass
            else:
                leave.total_time = int(leave.total_time) + 0.5
            leave.total = function.get_day(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)
            leave.rate = function.get_rate(leave.category, leave.other_reason)
            #get user
            if id==0:
                leave.user_id = models.User.objects.get(id=request.session['user_id'])
            #insert
            leave.save()
            message = "申請成功"
            #redirect
            return render(request, 'login/index.html', locals())
    if id==0:
        leave_form = forms.LeaveForm()
    else:
        leave_form = forms.LeaveForm(initial={'year':leave.year, 'month':leave.month, 'start':leave.start, 'end':leave.end,
                                                'category':leave.category, 'other_reason':leave.other_reason,
                                                'special':leave.special})
    return render(request, 'login/leave.html', locals())

def leave_list(request):
    checked = "已核准假單"
    unchecked = "未核准假單"
    checks = models.Leave.objects.filter(user_id=request.session['user_id'], checked=True)
    n_checks = models.Leave.objects.filter(user_id=request.session['user_id'], checked=False)
    apply = "請假申請"
    href = "/leave/"
    title = "leave"
    return render(request, 'login/list.html', locals())

def show_leave(request, id):
    user = models.User.objects.get(id=request.session['user_id'])
    try:
        leave = models.Leave.objects.get(id=id)
    except:
        return redirect("/leave_list/")
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if request.session['user_id'] == leave.user_id.id or (request.session['is_manager'] and user.department == leave.user_id.department) or request.session['is_hr']:
        return render(request, "login/display_leave.html", locals())
    else:
        redirect("/leave_list/")


def overtime(request, id=0):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if id!=0:
        overtime = models.Overtime.objects.get(id=id)
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
            date = datetime.datetime(overtime.year, overtime.month, overtime.day)
            if date.isoweekday() == 7:
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
                    overtime.one_third = 120
                    overtime.two_third = 360
                    overtime.double = total_minute - 480
            #get user
            if id==0:
                overtime.user_id = models.User.objects.get(id=request.session['user_id'])
            #insert
            overtime.checked = False
            overtime.save()
            message = "申請成功"
            #redirect
            return render(request, 'login/index.html', locals())
        else:
            return render(request, 'login/index.html', locals())
    if id==0:
        overtime_form = forms.OvertimeForm()
    else:
        overtime_form = forms.OvertimeForm(initial={ 'year':overtime.year, 'month':overtime.month, 'day':overtime.day, 'start':overtime.start, 'end':overtime.end,
                                                'reason':overtime.reason,})
    return render(request, 'login/overtime.html', locals())

def overtime_list(request):
    checked = "已核准加班單"
    unchecked = "未核准加班單"
    checks = models.Overtime.objects.filter(user_id=request.session['user_id'], checked=True)
    n_checks = models.Overtime.objects.filter(user_id=request.session['user_id'], checked=False)
    apply = "加班申請"
    href = "/overtime/"
    title = "overtime"
    return render(request, 'login/list.html', locals())

def show_overtime(request, id):
    user = models.User.objects.get(id=request.session['user_id'])
    try:
        overtime = models.Overtime.objects.get(id=id)
    except:
        return redirect("/overtime_list/")
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if request.session['user_id'] == overtime.user_id.id or (request.session['is_manager'] and user.department == overtime.user_id.department) or request.session['is_hr']:
        return render(request, "login/display_overtime.html", locals())
    else:
        redirect("/leave_list/")


def check_list(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if not request.session.get('is_manager', None) and not request.session.get('is_boss', None):
        message = "您沒有權限"
        return render(request, 'login/index.html', {'message':message})
    user = models.User.objects.get(id=request.session['user_id'])
    if user.boss:
        n_leaves = models.Leave.objects.filter(user_id__manager=True, checked=False)
        leaves = models.Leave.objects.filter(user_id__manager=True, checked=True)
        n_overtimes = models.Overtime.objects.filter(user_id__manager=True, checked=False)
        overtimes = models.Overtime.objects.filter(user_id__manager=True, checked=True)
    
    else:
        n_leaves = models.Leave.objects.filter(checked=False, user_id__department=user.department).exclude(user_id=user.id)
        leaves = models.Leave.objects.filter(checked=True, user_id__department=user.department).exclude(user_id=user.id)
        n_overtimes = models.Overtime.objects.filter(checked=False, user_id__department=user.department).exclude(user_id=user.id)
        overtimes = models.Overtime.objects.filter(checked=True, user_id__department=user.department).exclude(user_id=user.id)
    
    return render(request, 'login/check_list.html', locals())

def check(request):
    if request.method=="POST":
        id =request.POST['form_id']
        form_type = request.POST['form_type']
        if form_type == "leave":
            leave = models.Leave.objects.get(id=id)
            leave.checked = True
            leave.save()
        else:
            overtime = models.Overtime.objects.get(id=id)
            overtime.checked = True
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
    users = models.User.objects.all()
    return render(request, 'hr/hr_profile.html', locals())

def hr_personal(request, id):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    try:
        user = models.User.objects.get(id=id)
    except:
        return redirect("/hr/profile/")
    back = "/hr/profile/"
    return render(request, 'login/profile.html', locals())

def hr_edit(request, id):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
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
            user.retire_self = function.retire_M(user.retirement)*user.self_percent/100
            user.annual = function.get_annual(user.on_job.year, user.on_job.month, user.on_job.day)
            user.annual_left = user.annual - 0
            user.save()
            return redirect(f'/hr/profile/{user.id}/')
    func = "edit"
    title = "修改資料"
    action = f"/hr/edit/{id}/"
    user = models.User.objects.get(id=id)
    register_form = forms.SignUp(initial={'name':user.name, 'email':user.email, 'user_id':user.user_id,
                        'passwd':user.passwd, 'department':user.department,
                        'on_job':user.on_job, 'salary':user.salary, 'boss':user.boss, 'hr':user.hr,
                        'manager':user.manager, 'staff':user.staff, 'retire_self':user.self_percent,})
    back = f"/hr/profile/{user.id}/"
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
            new_User.retire_self = function.retire_M(new_User.retirement)*new_User.self_percent/100
            new_User.annual = function.get_annual(new_User.on_job.year, new_User.on_job.month, new_User.on_job.day)
            new_User.annual_left = new_User.annual - 0
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
        return redirect("/index/")
    if id==0:
        mode = "user"
        title = "請選擇員工"
        href = "/hr/attendance"
        back = "/hr/menu/"
        objects = models.User.objects.all()
        return render(request, 'hr/list.html', locals())
    else:
        dailys = models.Daily.objects.filter(user_id__id=id)
        back = "/hr/menu/"
        return render(request, 'login/attendance.html', locals())

def hr_leave(request, id=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if id == 0:
        mode = "user"
        objects = models.User.objects.all()
        title = "請選擇員工"
        href = "/hr/leave"
        back = "/hr/menu/"
        return render(request, 'hr/list.html', locals())
    else:
        mode = "leave"
        users = models.User.objects.get(id=id)
        objects = models.Leave.objects.filter(user_id=id, checked=True)
        title = f"{users.name}的已核准價單"
        href = "/display_leave"
        back = "/hr/leave/"
        return render(request, 'hr/list.html', locals())

def hr_overtime(request, id=0):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if id == 0:
        mode = "user"
        objects = models.User.objects.all()
        title = "請選擇員工"
        href = "/hr/overtime"
        back = "/hr/menu/"
        return render(request, 'hr/list.html', locals())
    else:
        mode = "overtime"
        users = models.User.objects.get(id=id)
        objects = models.Overtime.objects.filter(user_id=id, checked=True)
        title = f"{users.name}的已核准加班單"
        href = "/display_overtime"
        back = "/hr/overtime/"
        return render(request, 'hr/list.html', locals())

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
            Users = models.User.objects.all().exclude(name="admin")
            for user in Users:
                try:
                    total = models.Total.objects.get(user_id__id=user.id, month=month, year=year)
                except:
                    total = models.Total()
                    total.user_id = user
                #overtime
                Overtimes = models.Overtime.objects.filter(user_id__id=user.id, month=month, year=year)
                over_13 = 0
                over_23 = 0
                over_223 = 0
                over_2 = 0
                for overtime in Overtimes:
                    over_13 += overtime.one_third
                    over_23 += overtime.two_third
                    if datetime.datetime(overtime.year, overtime.month, overtime.day).isoweekday() == 7:
                        over_2 += overtime.double
                    else:
                        over_223 += overtime.double
                total.over_13 = over_13
                total.over_23 = over_23
                total.over_223 = over_223
                total.over_2 = over_2
                #leave
                Leaves = models.Leave.objects.filter(user_id__id=user.id, month=month, year=year)
                leave00 = 0
                leave01 = 0
                leave10 = 0
                for leave in Leaves:
                    if leave.rate == 0:
                        leave10 += leave.total_time
                    elif leave.rate == 0.5:
                        leave01 += leave.total_time
                    else:
                        leave00 += leave.total_time
                total.leave00 = leave00
                total.leave01 = leave01
                total.leave10 = leave10
                #late
                Dailys = models.Daily.objects.filter(user_id__id=user.id, month=month, year=year)
                leave_early = 0
                for daily in Dailys:
                    leave_early += daily.leave_early_fixed
                total.leave_early = leave_early
                hour_rate = float(user.salary)/float(30*8)
                minute_rate = float(hour_rate)/float(60)
                add = (minute_rate*4/3)*over_13 + (minute_rate*5/3)*over_23 + (minute_rate*8/3)*over_223 + (minute_rate*2)*over_2
                decrease = (hour_rate*0.5)*leave01 + (hour_rate)*leave00 + (minute_rate)*leave_early 
                decrease += function.convert_labor(user.labor) + function.convert_health(user.health) + function.convert_retirement(user.retirement) + user.retire_self
                print(add)
                print(decrease)
                total.actual_salary = user.salary + add - decrease
                total.save()
            message = "計算成功"
            return render(request, "hr/hr_menu.html", locals())
    else:
        month_form = forms.MonthForm()
        return render(request, "hr/salary.html", locals())

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
            user = models.User.objects.get(user_id=user_id)
        except:
            message = "Wrong ID."
            return render(request, 'hr/check_in_out.html', {'message': message})
        try:
            daily = models.Daily.objects.get(user_id__id=user.id, day=now.day, month=now.month, year=now.year)
        except models.Daily.DoesNotExist:
            daily = None
        if daily == None:
            daily = models.Daily()
            daily.on_time = now
            daily.user_id = user
            daily.year = datetime.date.today().year
            daily.month = datetime.date.today().month
            daily.day = datetime.date.today().day
            daily.on_time_fixed = now
        daily.off_time = now
        daily.off_time_fixed = now
        daily.halfway = 0
        daily.leave_early = 0
        daily.fixed_note=""
        #get time
        on = daily.on_time
        off = daily.off_time
        daily.attend = function.get_hour(daily.year, daily.month, daily.day, on.hour, on.minute, daily.year, daily.month, daily.day, off.hour, off.minute)
        if off.hour >= 17:
            daily.overtime = function.get_minute(daily.year, daily.month, daily.day, 17, 0, daily.year, daily.month, daily.day, off.hour, off.minute)
        else:
            daily.overtime = 0
        if on.hour >= 8:
            daily.leave_early = function.get_minute(daily.year, daily.month, daily.day, 8, 0, daily.year, daily.month, daily.day, on.hour, on.minute)
        else:
            daily.leave_early = 0
        if off.hour < 17:
            daily.leave_early = daily.leave_early + function.get_minute(daily.year, daily.month, daily.day, off.hour, off.minute, daily.year, daily.month, daily.day, 17, 0)
        else:
            daily.leave_early = daily.leave_early
        daily.attend_fixed = daily.attend
        daily.overtime_fixed = daily.overtime
        daily.leave_early_fixed = daily.leave_early
        daily.save()
        #else:
        #    daily.off_time = now
        #    daily.save()
        message = f"{user.name}簽到成功"
    return render(request, 'hr/check_in_out.html', {'message': message})