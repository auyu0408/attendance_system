from django.db.models.expressions import F
from attendance.views import overtime
from django.db import models
from datetime import date, datetime
from django.db.models import base
from django.db.models.deletion import CASCADE
from django.utils import timezone
import time

# Create your models here.
class User(models.Model):
    #Fields
    class Department(models.TextChoices):
        業務部 = '業務部'
        人事部 = '人事部'
        會計部 = '會計部'
        admin = 'admin'
        管理部 = 'BOSS'

    name = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256, unique=True)
    passwd = models.CharField(max_length=256)
    email = models.EmailField(max_length=254, unique=True)
    department = models.CharField(max_length=128)
    on_job = models.DateField(auto_now=False, auto_now_add=False, default=date.today)
    salary = models.PositiveIntegerField()
    annual = models.PositiveSmallIntegerField(default=0)
    annual_left = models.PositiveSmallIntegerField(default=0)
    #Deductible 
    labor = models.PositiveSmallIntegerField(default=1)
    health = models.PositiveSmallIntegerField(default=1)
    family = models.PositiveSmallIntegerField(default=0)
    retirement = models.PositiveSmallIntegerField(default=1)
    self_percent =models.PositiveSmallIntegerField(default=0)
    retire_self = models.PositiveSmallIntegerField(default=0)
    ##identity check
    boss = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    hr = models.BooleanField(default=False)
    staff = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(default=0)#在職=0,離職=1,留職停薪=2
    #Meta
    class Meta:
        ordering = ['on_job']
    #Methods

class Leave(models.Model):
    #Fields
    class Reason(models.TextChoices):
        病假 = '病假'#0.5
        生理假 = '生理假'#0.5
        事假 = '事假'#1
        家庭照顧假 = '家庭照顧假'#1
        育嬰假 = '育嬰假'
        無薪假 = '無薪假'#1
        防疫隔離假 = '防疫隔離假'#1
        防疫照顧假 = '防疫照顧假'#1
        疫苗接種假 = '疫苗接種假'#1
        因公隔離 = '因公隔離'#0.5
        出差 = '出差'
        公假 = '公假'
        工傷假 = '工傷假'
        喪假 = '喪假'
        婚假 = '婚假'
        產假 = '產假'
        陪產假 = '陪產假'
        產前假 = '產前假'
        特休 = '特休'
        補休 = '補休'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=0)
    month = models.PositiveSmallIntegerField(default=0)
    start = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    end = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    total_time = models.FloatField(default=0, help_text='in hours')
    total = models.FloatField(default=0, help_text='in days')
    category = models.CharField(max_length=64, choices=Reason.choices, default=Reason.特休)
    special = models.TextField(blank=True, null=True)
    checked = models.BooleanField(default=False)
    double_check = models.BooleanField(default=False)
    #Meta
    class Meta:
        ordering = ['-start']
    #Methods

class Overtime(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=0)
    month = models.PositiveSmallIntegerField(default=0)
    day = models.PositiveSmallIntegerField(default=0)
    start = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    end = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    one_third = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    two_third = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    double = models.PositiveSmallIntegerField(default=0, help_text='in hours')
    reason = models.CharField(max_length=256, blank=True, null=True)
    checked = models.BooleanField(default=False)
    double_check = models.BooleanField(default=False)
    #Meta
    class Meta:
        ordering = ['-year', '-month', '-day']
    #Methods

class Daily(models.Model):
    #Field
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(default=0)
    month = models.PositiveSmallIntegerField(default=0)
    day = models.PositiveSmallIntegerField(default=0)
    on_time = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    off_time = models.TimeField(auto_now=False, auto_now_add=False, default=timezone.now)
    on_time_fixed = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    off_time_fixed = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    attend = models.FloatField(default=0)
    overtime = models.PositiveSmallIntegerField(default=0)
    leave_early = models.PositiveSmallIntegerField(default=0)
    attend_fixed = models.FloatField(default=0)
    overtime_fixed = models.PositiveSmallIntegerField(default=0)
    leave_early_fixed = models.PositiveSmallIntegerField(default=0)
    holiday = models.CharField(max_length=256, blank=True, null=True)
    fixed_note = models.CharField(max_length=256, blank=True, null=True)
    #Meta
    class Meta:
        ordering = ['-year', '-month', '-day']
    #Method

class Total_leave(models.Model):
    sick = models.FloatField(default=0)#hour
    sick_deduce = models.PositiveIntegerField(default=0)
    menstrual = models.FloatField(default=0)#hour
    menstrual_deduce = models.PositiveIntegerField(default=0)
    personal = models.FloatField(default=0)#hour
    personal_deduce = models.PositiveIntegerField(default=0)
    takecare = models.FloatField(default=0)#hour
    care_deduce = models.PositiveIntegerField(default=0)
    nursery = models.FloatField(default=0)#day
    nursery_deduce = models.PositiveIntegerField(default=0)
    unpaid = models.FloatField(default=0)#day
    unpaid_deduce = models.PositiveIntegerField(default=0)
    other1 = models.FloatField(default=0)#day
    other1_deduce = models.PositiveIntegerField(default=0)
    other2 = models.FloatField(default=0)#hour
    other2_deduce = models.PositiveIntegerField(default=0)
    other3 = models.FloatField(default=0)#hour
    other3_deduce = models.PositiveIntegerField(default=0)
    other4 = models.FloatField(default=0)#day
    other4_deduce = models.PositiveIntegerField(default=0)
    business = models.FloatField(default=0)#day
    official = models.FloatField(default=0)#day
    injury = models.FloatField(default=0)#day
    funeral = models.FloatField(default=0)#day
    marriage = models.FloatField(default=0)#day
    maternity = models.FloatField(default=0)#day
    paternity = models.FloatField(default=0)#day
    prenatal = models.FloatField(default=0)#day
    annual = models.FloatField(default=0)#day
    rest = models.FloatField(default=0)#day

class Total(models.Model):
    #Field
    user_id = models.ForeignKey(User, on_delete=CASCADE)
    year = models.PositiveSmallIntegerField(default=time.localtime(time.time()).tm_year)
    month = models.PositiveSmallIntegerField(default=time.localtime(time.time()).tm_mon)
    #delaytime = models.PositiveIntegerField(default=0)#hours
    over_13 = models.PositiveSmallIntegerField(default=0)
    over_23 = models.PositiveSmallIntegerField(default=0)
    over_613 = models.PositiveSmallIntegerField(default=0)
    over_623 = models.PositiveSmallIntegerField(default=0)
    over_223 = models.PositiveSmallIntegerField(default=0)
    over_2  = models.PositiveSmallIntegerField(default=0)
    total_leave = models.ForeignKey(Total_leave, on_delete=CASCADE)
    decrease = models.PositiveIntegerField(default=0)#應扣金額
    leave_early = models.PositiveIntegerField(default=0)
    tax = models.PositiveIntegerField(default=0)
    absence = models.PositiveSmallIntegerField(default=0)#曠工
    actual_salary = models.IntegerField(default=0)
    #Meta
    class Meta:
        ordering = ['-year', '-month']
    #Method