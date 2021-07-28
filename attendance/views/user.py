# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from django.contrib.auth.hashers import check_password, make_password
from attendance import function

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
    date = datetime.date.today()
    user.seniority = function.get_seniority(user.on_job.year, user.on_job.month, user.on_job.day, date.year, date.month, date.day)
    user.annual = function.get_annual(user.seniority)
    user.save()
    if date > datetime.date(date.year, user.on_job.month, user.on_job.day):
        due = date.year
    else:
        due = date.year - 1
    Annual_leave = models.Leave.objects.filter(category="特休", start__gte=datetime.datetime(due,user.on_job.month,user.on_job.day), user_id=user)
    annual = 0
    for obj in Annual_leave:
        annual += obj.total
    annual_left = user.annual-annual
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

def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    #delete session
    request.session.flush()
    return redirect("/login/")

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