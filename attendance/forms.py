from django import forms
from datetime import date

from django.forms.widgets import CheckboxInput, TimeInput

class SignUp(forms.Form):
    
    name = forms.CharField(label="Name", max_length=128, widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    user_id = forms.CharField(label="ID", max_length=256, widget=forms.TextInput(attrs={'class':'form-control'}))
    passwd = forms.CharField(label="Password", max_length=256, required=False, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    #branch = forms.CharField(max_length=256)#分公司
    email = forms.EmailField(label="E-mail", max_length=254, widget=forms.EmailInput(attrs={'class':'form-control'}))
    department = forms.CharField(label="Department", max_length=128, widget=forms.TextInput(attrs={'class':'form-control'}))
    on_job = forms.DateField(label="On job", widget=forms.DateInput(attrs={'class':'form-control'}))
    salary = forms.IntegerField(label="Basic Salary", widget=forms.TextInput(attrs={'class':'form-control'}))
    ##identity check
    boss = forms.BooleanField(label="Boss", required=False)
    hr = forms.BooleanField(label="HR", required=False)
    manager = forms.BooleanField(label="Manager", required=False)
    staff = forms.BooleanField(label="Staff", required=True)
    self_percent = forms.IntegerField(label="Self", widget=forms.TextInput(attrs={'class':'form-control'}),initial=0)

class LeaveForm(forms.Form):
    Reason=(
        ('SICK', '病假'),
        ('PERSONAL', '事假'),
        ('ANNUAL', '特休'),
        ('OFFICIAL', '公假'),
        ('FUNERAL', '喪假'),
        ('MARRIAGE', '婚假'),
        ('MENSTRUAL', '生理假'),
        ('MATERNITY', '產前假'),
        ('PATERNITY', '陪產假'),
        ('INJURY', '職災病假'),
        ('OTHER', '其他'),
    )

    year = forms.IntegerField(label="年", widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    month = forms.IntegerField(label="月", widget=forms.TextInput(attrs={'class':'form-control'}))
    start = forms.DateTimeField(label="start", widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    end = forms.DateTimeField(label="end", widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    category = forms.ChoiceField(label="假別", choices=Reason)
    other_reason = forms.CharField(label="特殊假別", widget=forms.TextInput(attrs={'class':'form-control'}), required=False)
    special = forms.CharField(label="證明", required=False, widget=forms.Textarea(attrs={'class':'form-control'}))

class OvertimeForm(forms.Form):
    year = forms.IntegerField(label="年", widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    month = forms.IntegerField(label="月", widget=forms.TextInput(attrs={'class':'form-control'}))
    day = forms.IntegerField(label="日", widget=forms.TextInput(attrs={'class':'form-control'}))
    start = forms.TimeField(label="start time", widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    end = forms.TimeField(label="end time", widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    reason = forms.CharField(label="原因", widget=forms.TextInput(attrs={'class':'form-control'}), required=False)

class Passwd(forms.Form):
    origin = forms.CharField(label="原密碼", widget=forms.PasswordInput(attrs={'class':'form-control', 'autofocus':''}))
    new = forms.CharField(label="新密碼", widget=forms.PasswordInput(attrs={'class':'form-control'}))

class DailyForm(forms.Form):
    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    on_time = forms.TimeField(label="上班時間", widget=forms.TimeInput(attrs={'class':'form-control'}))
    off_time = forms.TimeField(label="下班時間", widget=forms.TimeInput(attrs={'class':'form-control'}))
    on_time_fixed = forms.TimeField(label="上班時間(實際)", widget=forms.TimeInput(attrs={'class':'form-control'}), required=False)
    off_time_fixed = forms.TimeField(label="下班時間(實際)",widget=forms.TimeInput(attrs={'class':'form-control'}), required=False)
    fixed_note = forms.CharField(label="備註", widget=forms.TextInput(attrs={'class':'form-control'}), required=False)
    year = forms.IntegerField(label="年", widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    month = forms.IntegerField(label="月", widget=forms.TextInput(attrs={'class':'form-control'}))
    day = forms.IntegerField(label="日", widget=forms.TextInput(attrs={'class':'form-control'}))

class MonthForm(forms.Form):
    year = forms.IntegerField(label="年", widget=forms.TextInput(attrs={'class':'form-control','autofocus':''}))
    month = forms.IntegerField(label="月", widget=forms.TextInput(attrs={'class':'form-control'}))