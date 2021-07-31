# attendance_system  

一個模擬出勤系統的應用，用python django，但還沒很會所以可能有點凌亂  

## Set up  

### Prerequisites  

- Python 3.7  
- pipenv(Python Module)  

### Environment Setup  

  1. initialize python environment  
  ```
  make init
  ```  
  2. Database migrate(sqlite)  
  ```
  make migrate
  ```
  3. Start the service  
  ```
  pipenv run python manage.py runserver
  ```  
  The server will run at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
  4. Stop service  
  ```
  Ctrl+c
  ```  
  5. Delete Database  
  ```
  make clean
  ```  

## Use  

### Get admin  

- Login panel:
  - at first, you don't have any  user, click here to add an admin.  
  ![](https://i.imgur.com/Iuev2yx.png)
  - default account:  
    - ID: `admin`  
    - password: `admin`  
  - only thing you can change is admin password.  
- index menu
  - After you login with admin, you can see:  
![](https://i.imgur.com/3u5fFqG.png)

  - Create new User with `人事>人事資料建檔` or URL path: `/hr/register/`
  - you need to have hr identity when you want to enter hr pages.
- hr menu
  - 和薪資相關的功能需要輸入薪資密碼才能觀看，薪資密碼即是admin密碼，可更改  
  - 打卡功能是只要輸入ID即可打卡，概念是可以接讀卡機抓卡號  
    ![](https://i.imgur.com/3Q1MM5a.png)

### Identity:  

- there have four kinds of identity, boss, hr, manager, staff
- there also have some department, such as: 業務部1, 業務部2, 人事部, 會計部, boss
- 以下是各個身份的頁面  
  - staff  
![](https://i.imgur.com/aspt7Fj.png)

  - manager  
![](https://i.imgur.com/od5ReIh.png)

  - hr  
![](https://i.imgur.com/EUcgzEK.png)

  - boss  
![](https://i.imgur.com/RC6TCJj.png)

- manager 能看到的假單和加班單是自己部門底下的職員，boss則能看到manager身份的  
- manager不能批准自己的假單和加班單，boss可以
- admin有staff, manager和hr的身份

## Material  

- [self](https://github.com/auyu0408)
