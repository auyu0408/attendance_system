# attendance_system  
一個模擬出勤系統的應用，用python django，但還沒很會所以可能有點凌亂  
## Set up  

### Prerequires  
- python 3.7 (or above) 
- django  3.1 (or above)
### Getting Start
```python
python manager.py migrate  
#python manager.py createsuperuser
python manage.py runserver
```
- them, enter `http://127.0.0.1:8080`, or you have other setting with this application
## Use  

### Set admin
- Login panel:
  - at first, you don't have any  user, click here to add an admin.  
  - default account:  
    -  ID: `admin`  
    -  password: `admin`  
  - only thing you can change is admin's password.  
- index menu
  - after, you login with admin, you can see:  
  - you can create new user with `人事>人事資料建檔` or URLpath: `/hr/register/`
  - you need to have hr identity when you want to enter any hr pages.
- salary
  - 和薪資相關的菇能需要輸入薪資密碼才能觀看，薪資密碼即是admin密碼，可更改  
### Identity:  
- there have four kinds of identity, boss, hr, manager, staff
- there also have some department, such as: 業務部1, 業務部2, 人事部, 會計部, boss
- 以下是各個身份的界面
  - staff
  - manager
  - hr
  - boss
- manager 能看到的假單和加班單是自己部門底下的職員，boss則能看到manager身份的
- manager不能批准自己的假單和加班單，boss可以
- admin有staff, manager和hr的身份
