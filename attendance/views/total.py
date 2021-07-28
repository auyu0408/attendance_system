# -*- coding: UTF-8 -*-
import datetime
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms
from attendance import function

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
    user = total.user_id
    today = datetime.date.today()
    seniority = function.get_seniority(user.on_job.year, user.on_job.month, user.on_job.day, total.year, total.month+1, 1)
    annual = function.get_annual(seniority)
    labor = function.convert_labor(user.labor)
    health = function.convert_health(user.health)
    retire = function.convert_retirement(user.retirement)
    tax_over = round(total.tax_over/60,2)
    free_over = round(total.free_over/60,2)
    if datetime.date.today() > datetime.date(total.year, user.on_job.month, user.on_job.day):
        due = datetime.date.today().year-1
    else:
        due = datetime.date.today().year
    Annual_leave = models.Leave.objects.filter(start__gte=datetime.datetime(due,user.on_job.month,user.on_job.day), user_id=user, category="特休").exclude(start__gte=datetime.datetime(total.year, total.month+1, 1))
    day = 0
    for obj in Annual_leave:
        day += obj.total
    annual_left = annual-day
    return render(request, "hr/display_total.html", locals())