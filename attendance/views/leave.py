# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from attendance import function

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
        if leave.category != "特休":
            Other = models.Leave.objects.filter(user_id=leave.user_id, category=leave.category, year=leave.year)
            day = 0
            for obj in Other:
                day += obj.total
            if leave.category == "病假":
                str = "可休30天"
            elif leave.category == "事假":
                str = "可休14天"
            else:
                str = ""
        else:
            user = leave.user_id
            if leave.start > datetime.datetime(leave.year, user.on_job.month, user.on_job.day):
                due = leave.year
            else:
                due = leave.year - 1
            annual = function.get_annual(function.get_seniority(user.on_job.year, user.on_job.month, user.on_job.day, leave.year, leave.month, leave.start.day))
            Annual = models.Leave.objects.filter(user_id=user, start__gte=datetime.datetime(due, user.on_job.month, user.on_job.day), category=leave.category).exclude(start__gt=leave.start)
            day = 0
            str = f"可休{annual}天"
            for obj in Annual:
                day += obj.total
    except:
        return redirect("/leave_list/")
    if request.session['user_id'] == leave.user_id.id or (request.session['is_manager'] and user.department == leave.user_id.department) or request.session['is_hr']:
        return render(request, "login/display_leave.html", locals())
    else:
        return redirect("/leave_list/")

def delete_leave(request, id):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    try:
        leave = models.Leave.objects.get(id=id)
        if request.session['user_id'] == leave.user_id.id:
            pass
        else:
            return redirect("/leave_list/")
    except:
        return redirect("/leave_list/")
    day = leave.end.day - leave.start.day
    if day == 0:
        try:
            daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=leave.start.day, user_id=leave.user_id)
        except:
            pass
        daily.holiday -= 0
        daily.holiday_reason = ""
        daily.check = False
        daily.save()
    else:
        for date in range(leave.start.day, leave.end.day+1):
            try:
                daily = models.Daily.objects.get(year=leave.year, month=leave.month, day=date, user_id=leave.user_id)
            except:
                continue
            daily.holiday = 0
            daily.holiday_reason = ""
            daily.check = False
            daily.save()
    leave.delete()
    return redirect("/leave_list/")

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
        for obj in objects:
            if obj.category != "特休":
                Others = models.Leave.objects.filter(user_id=user, category=obj.category, year=obj.year)
                day = 0
                for other in Others:
                    day += other.total
                if obj.category == "病假":
                    str = "可休30天"
                elif obj.category == "事假":
                    str = "可休14天"
                else:
                    str = ""
                obj.str = f"{str} 已休{day}天"
            else:
                if obj.start > datetime.datetime(obj.year, user.on_job.month, user.on_job.day):
                    due = obj.year
                else:
                    due = obj.year - 1
                annual = function.get_annual(function.get_seniority(user.on_job.year, user.on_job.month, user.on_job.day, obj.year, obj.month, obj.start.day))
                Annual = models.Leave.objects.filter(user_id=user, start__gte=datetime.datetime(due, user.on_job.month, user.on_job.day), category=obj.category).exclude(start__gt=obj.start)
                day = 0
                str = f"可休{annual}天"
                for other in Annual:
                    day += other.total
                obj.str = f"{str} 已休{day}天"
        return render(request, 'hr/list.html', locals())