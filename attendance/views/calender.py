# -*- coding: UTF-8 -*-
from django.http import request
from django.shortcuts import redirect, render
from attendance import models
from attendance import forms

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