from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from . import models
from . import forms
from django.contrib.auth.hashers import check_password, make_password

# Create your views here.
def index(request):
    pass
    return render(request, 'login/index.html')

def login(request):
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
                print(user_id, passwd)
                return redirect('/index/')
            else:
                message = 'Wrong passwd!'
                return render(request, 'login/login.html', {'message': message})
        else:
            return render(request, 'login/login.html', {'message': message})
    return render(request, 'login/login.html')

def register(request):
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
                return render(request, 'login/register.html', locals())
            same_email = models.User.objects.filter(email=email)
            if same_email:
                message = 'Same E-mail.'
                return render(request, 'login/register.html', locals())
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
            return redirect('/index/')
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.SignUp()
    return render(request, 'login/register.html', locals()) 

def logout(request):
    pass
    return redirect("/login/")

def attendance_record(request):
    pass
    return render(request, 'login/attendance_record.html')

def leave_form(request):
    pass
    return render(request, 'login/leave_form.html')