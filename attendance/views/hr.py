# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from django.contrib.auth.hashers import make_password
from attendance import function

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