from django.core.checks import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from . import models
from . import forms
from django.contrib.auth.hashers import check_password, make_password

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
    return render(request, 'login/profile.html', locals())

def change_passwd(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
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

def leave(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
        
    if request.method == 'POST':
        leave_form = forms.LeaveForm(request.POST)
        message = "please check the input type"
        if leave_form.is_valid():
            start_time = leave_form.cleaned_data.get('start_time')
            end_time = leave_form.cleaned_data.get('end_time')
            category = leave_form.cleaned_data.get('category')
            other_reason = leave_form.cleaned_data.get('other_reason')
            special = leave_form.cleaned_data.get('special')
        #get user
        user_id = models.User.objects.get(id=request.session['user_id'])
        #insert
        new_leave = models.Leave()
        new_leave.user_id = user_id
        new_leave.start_time = start_time
        new_leave.end_time = end_time
        new_leave.category = category
        new_leave.other_reason = other_reason
        new_leave.special = special
        new_leave.check = False
        new_leave.save()
        message = "申請成功"
        #redirect
        return render(request, 'login/index.html', locals())
    leave_form = forms.LeaveForm()
    return render(request, 'login/leave.html', locals())

def overtime(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
        
    if request.method == 'POST':
        overtime_form = forms.OvertimeForm(request.POST)
        message = "please check the input type"
        if overtime_form.is_valid():
            start_time = overtime_form.cleaned_data.get('start_time')
            end_time = overtime_form.cleaned_data.get('end_time')
            reason = overtime_form.cleaned_data.get('reason')
        #get user
        user_id = models.User.objects.get(id=request.session['user_id'])
        #insert
        new_overtime = models.Overtime()
        new_overtime.user_id = user_id
        new_overtime.start_time = start_time
        new_overtime.end_time = end_time
        new_overtime.reason = reason
        new_overtime.one_third = 0
        new_overtime.two_third = 0
        new_overtime.double = 0
        new_overtime.check = False
        new_overtime.save()
        message = "申請成功"
        #redirect
        return render(request, 'login/index.html', locals())
    overtime_form = forms.OvertimeForm()
    return render(request, 'login/overtime.html', locals())

def check(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'login/check.html')

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
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/hr_menu.html')

def hr_profile(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/hr_profile.html')

def hr_register(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    if request.method == 'POST':
        register_form = forms.SignUp(request.POST)
        message = "please check input type."
        if register_form.is_valid():
            name = register_form.cleaned_data.get('name')
            user_id = register_form.cleaned_data.get('user_id')
            passwd = register_form.cleaned_data.get('passwd')
            email = register_form.cleaned_data.get('email')
            department =register_form.cleaned_data.get('department')
            on_job = register_form.cleaned_data.get('on_job')
            salary = register_form.cleaned_data.get('salary')
            boss = register_form.cleaned_data.get('boss')
            hr = register_form.cleaned_data.get('hr')
            manager = register_form.cleaned_data.get('manager')
            staff = register_form.cleaned_data.get('staff')
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
            new_User = models.User()
            new_User.name = name
            new_User.user_id = user_id
            new_User.passwd = password
            new_User.email = email
            new_User.department = department
            new_User.salary = salary
            new_User.on_job = on_job
            new_User.annual = 0
            new_User.boss = boss
            new_User.hr = hr
            new_User.manager = manager
            new_User.staff = staff
            new_User.save()
            #redirect
            return redirect('/hr/menu/')
        else:
            return render(request, 'hr/register.html', locals())
    register_form = forms.SignUp()
    return render(request, 'hr/register.html', locals()) 
    
def hr_attendance(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/attendance.html')

def hr_leave(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/leave.html')

def hr_salary(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/salary.html')

def hr_bonus(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    return render(request, 'hr/bonus.html')