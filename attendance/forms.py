from django import forms
from datetime import date

from django.forms.widgets import CheckboxInput

class SignUp(forms.Form):
    
    name = forms.CharField(label="Name", max_length=128, widget=forms.TextInput(attrs={'class':'form-control', 'autofocus':''}))
    user_id = forms.CharField(label="ID", max_length=256, widget=forms.TextInput(attrs={'class':'form-control'}))
    passwd = forms.CharField(label="Password", max_length=256, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    #branch = models.CharField(max_length=256)#分公司
    email = forms.EmailField(label="E-mail", max_length=254, widget=forms.EmailInput(attrs={'class':'form-control'}))
    department = forms.CharField(label="Department", max_length=128, widget=forms.TextInput(attrs={'class':'form-control'}))
    on_job = forms.DateField(label="On job", widget=forms.DateInput(attrs={'class':'form-control'}))
    salary = forms.IntegerField(label="Basic Salary", widget=forms.TextInput(attrs={'class':'form-control'}))
    ##identity check
    boss = forms.BooleanField(label="Boss", required=False)
    hr = forms.BooleanField(label="HR", required=False)
    manager = forms.BooleanField(label="Manager", required=False)                                                                                                                       )
    staff = forms.BooleanField(label="Staff", required=True)

class LeaveForm(forms.Form):
    class Reason(forms.TextChoices):
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

    start_time = forms.DateTimeField(label="start time", widget=forms.DateTimeInput(attrs={'class':'form-control', 'autofocus':''}))
    end_time = forms.DateTimeField(label="end time", widget=forms.DateTimeInput(attrs={'class':'form-control'}))
    category = forms.CharField(label="假別", widget=forms.TextInput(attrs={'class':'form-control'}))
    other_reason = forms.CharField(label="原因", widget=forms.TextInput(attrs={'class':'form-control'}), required=False)
    special = forms.TextField(label="證明", widget=forms.TextInput(attrs={'class':'form-control'}))