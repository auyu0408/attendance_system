# -*- coding: UTF-8 -*-
from django.core.checks import messages
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from . import models
from . import forms
from django.contrib.auth.hashers import check_password, make_password
from . import function

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
    return render(request, 'login/attendance.html')


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
            s = leave_form.cleaned_data.get('start_time')
            e = leave_form.cleaned_data.get('end_time')
            leave.start_time = s
            leave.end_time = e
            leave.category = leave_form.cleaned_data.get('category')
            leave.other_reason = leave_form.cleaned_data.get('other_reason')
            leave.special = leave_form.cleaned_data.get('special')
            leave.checked = False
            if leave.other_reason != "因公隔離" and leave.other_reason != "防疫照顧假" and leave.other_reason != "防疫隔離假" and leave.other_reason != "疫苗給薪假" and leave.other_reason != "":
                message = "Wrong reason type."
                return render(request, 'login/leave.html', {'message': message})
            #get total time
            leave.total_time = function.get_hour(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)
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
        leave_form = forms.LeaveForm(initial={'start_time':leave.start_time, 'end_time':leave.end_time,
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
            s = overtime_form.cleaned_data.get('start_time')
            e = overtime_form.cleaned_data.get('end_time')
            overtime.start_time = overtime_form.cleaned_data.get('start_time')
            overtime.end_time = overtime_form.cleaned_data.get('end_time')
            overtime.reason = overtime_form.cleaned_data.get('reason')
        # get time
        if overtime.start_time.isoweekday() == 7:
            overtime.double = function.get_sunday(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)
            overtime.one_third = 0
            overtime.two_third = 0
        else:
            total_minute = function.get_minute(s.year, s.month, s.day, s.hour, s.minute, e.year, e.month, e.day, e.hour, e.minute)
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
    if id==0:
        overtime_form = forms.OvertimeForm()
    else:
        overtime_form = forms.OvertimeForm(initial={'start_time':overtime.start_time, 'end_time':overtime.end_time,
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


def hr_attendance(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    return render(request, 'hr/attendance.html')

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
        mode = "leave"
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
    else:
        return render(request, "hr/salary.html")

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

def hr_bonus(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    if not request.session.get('is_salary', None):
        return redirect("/hr/salary_pass/")
    return render(request, 'hr/bonus.html')

def check_in_out(request):
    if not request.session.get('is_hr', None):
        return redirect("/index/")
    message = ""
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        try:
            user = models.User.objects.get(user_id=user_id)
        except:
            message = "Wrong ID."
            return render(request, 'hr/check_in_out.html', {'message': message})
        message = f"{user.name}簽到成功"
    return render(request, 'hr/check_in_out.html', {'message': message})