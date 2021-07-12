from django.db import models
from datetime import date, datetime
from django.db.models.deletion import CASCADE
from django.utils import timezone
import time

# Create your models here.
class User(models.Model):
    #Fields
    name = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256, unique=True)
    passwd = models.CharField(max_length=256)
    #branch = models.CharField(max_length=256)#分公司
    email = models.EmailField(max_length=254, unique=True)
    department = models.CharField(max_length=128)
    on_job = models.DateField(auto_now=False, auto_now_add=False, default=date.today)
    salary = models.PositiveIntegerField()
    annual_left = models.PositiveSmallIntegerField(default=0)
    ##identity check
    boss = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    hr = models.BooleanField(default=False)
    staff = models.BooleanField(default=True)
    #Meta
    class Meta:
        ordering = ['on_job']
    #Methods

class Leave(models.Model):
    #Fields
    class Reason(models.TextChoices):
        SICK = '病假'
        PERSONAL = '事假'
        ANNUAL = '特休'
        OFFICIAL = '公假'
        FUNERAL = '喪假'
        MARRIAGE = '婚假'
        MENSTRUAL = '生理假'
        MATERNITY = '產前假'
        PATERNITY = '陪產假'
        OTHER = '其他'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    total_time = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    total = models.PositiveSmallIntegerField(default=0, help_text='in days')
    category = models.CharField(max_length=64, choices=Reason.choices, default=Reason.ANNUAL)
    other_reason = models.CharField(max_length=128, blank=True, null=True, help_text='fill in when above is other' )#used when category=other
    special = models.TextField(blank=True, null=True)
    checked = models.BooleanField(default=False)
    #Meta
    class Meta:
        ordering = ['-start_time']
    #Methods

class Overtime(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    one_third = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    two_third = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    double = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    reason = models.CharField(max_length=256, blank=True, null=True)
    checked = models.BooleanField(default=False)
    #Meta
    class Meta:
        ordering = ['-start_time']
    #Methods

class Daily(models.Model):
    #Field
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    on_time = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    off_time = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    on_time_fixed = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    off_time_fixed = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    fixed_note = models.CharField(max_length=256, blank=True, null=True)
    #Meta
    class Meta:
        ordering = ['date']
    #Method

class Total(models.Model):
    #Field
    user_id = models.ForeignKey(User, on_delete=CASCADE)
    year = models.PositiveSmallIntegerField(default=time.localtime(time.time()).tm_year)
    month = models.PositiveSmallIntegerField(default=time.localtime(time.time()).tm_mon)
    #delaytime = models.PositiveIntegerField(default=0)#hours
    over_13 = models.PositiveSmallIntegerField(default=0)
    over_23 = models.PositiveSmallIntegerField(default=0)
    over_2  = models.PositiveSmallIntegerField(default=0)
    leave_00 = models.PositiveIntegerField(default=0)#no salary hours
    leave_01 = models.PositiveIntegerField(default=0)#half salary
    leave_10 = models.PositiveIntegerField(default=0)#full salary
    actual_salary = models.PositiveIntegerField(default=0)
    #Meta
    class Meta:
        ordering = ['-year', '-month']
    #Method