# -*- coding: UTF-8 -*-
import datetime
stander=[[0, 24000, 25200, 26400, 27600, 28800, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800, 48200, 50600, 53000, 55400, 57800, 60800, 63800, 66800, 69800, 72800, 76500, 80200, 83900, 87600, 92100, 96600, 101100, 105600, 110100, 115500, 120900, 126300, 131700, 137100, 142500, 147900, 150000, 156400, 162800, 169200, 175600, 182000],
        [ 0, 552,   579,   607,   635,   663,   697,   732,   766,   801,   835,   878,   922,   966,   1010,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054],
        [ 0, 372,   391,   409,   428,   447,   470,   493,   516,   540,   563,   592,   622,   651,   681,   710,   748,   785,   822,   859,   896,   943,   990,   1036,  1083,  1129,  1187,  1244,  1301,  1359,  1428,  1498,  1568,   1638,   1708,   1791,   1875,   1959,   2043,   2126,   2210,   2294,   2327,   2426,   2525,   2624,   2724,   2823],
        [ 0, 1440,  1512,  1584,  1656,  1728,  1818,  1908,  1998,  2088,  2178,  2292,  2406,  2520,  2634,  2748,  2892,  3036,  3180,  3324,  3468,  3648,  3828,  4008,  4188,  4368,  4590,  4812,  5034,  5256,  5526,  5796,  6066,   6336,   6606,   6930,   7254,   7578,   7902,   8226,   8550,   8874,   9000,   9000,   9000,   9000,   9000,   9000]]
annual = [180, ]


def convert_labor(level):
    labor_money = stander[1][level]
    return labor_money

def convert_health(level):
    health_money = stander[2][level]
    return health_money

def convert_retirement(level):
    retirement_money = stander[3][level]
    return retirement_money

def find_labor(money):
    for x in range(16):
        if stander[0][x]+1 > money:
            labor = x
            return labor
    labor = 15
    return labor

def find_health(money):
    for x in range(48):
        if stander[0][x]+1 > money:
            health = x
            return health
    health = 47
    return health

def find_retirement(money):
    for x in range(43):
        if stander[0][x]+1 > money:
            retirement = x
            return retirement
    retirement = 42
    return retirement

def retire_M(level):
    money = stander[0][level]
    return money

def get_annual(year,month,day):
    new_year = year
    new_month = month+6 
    if month+6 > 12:
        new_year = year +1
        new_month = month - 6
    if datetime.datetime.now() < datetime.datetime(new_year, new_month, day):
        annual = 0
    elif datetime.datetime.now() < datetime.datetime(year+1, month, day):
        annual = 3
    elif datetime.datetime.now() < datetime.datetime(year+2, month, day):
        annual = 7
    elif datetime.datetime.now() < datetime.datetime(year+3, month, day):
        annual = 10
    elif datetime.datetime.now() < datetime.datetime(year+5, month, day):
        annual = 14
    elif datetime.datetime.now() < datetime.datetime(year+10, month, day):
        annual = 15
    else:
        for i in range(11,25,1):
            if datetime.datetime.now() < datetime.datetime(year+i, month, day):
                annual = 5 + i
                break
        if datetime.datetime.now() >= datetime.datetime(year+25, month, day):
            annual = 30
    return annual

def get_day(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if sh == 12:
        sh = 13
        sm = 0
    if eh == 12:
        em = 0
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    hour = day1.seconds/60/60
    minute = (day1.seconds-hour*3600)/60
    if minute > 30:
        hour = hour + 1
    elif minute > 0:
        hour = hour + 0.5
    else:
        hour = hour
    if sh <12 and eh >12:
        hour = hour - 1
    day = day1.days + round(float(hour)/float(8),2)
    return day

def get_hour(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if sh == 12:
        sh = 13
        sm = 0
    if eh == 12:
        em = 0
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    hour1 = round(float(day1.seconds)/3600,2)
    minute = (day1.seconds-hour1*3600)/60
    if sh <12 and eh >12:
        hour1 = hour1 - 1
    hour = hour1 + day1.days*8
    return hour

def get_minute(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    minute = (day1.seconds)/60
    return minute

def get_weekend(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if sh == 12:
        sh = 13
        sm = 0
    if eh == 12:
        em = 0
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    minute = (day1.seconds)/60
    if sh <12 and eh >12:
        minute = minute - 60
    return minute

def get_rate(catogory, others):
    if catogory == "SICK" or (catogory == 'OTHERS' and others in'因公隔離'):
        rate = 0.5
    elif catogory == "MARRIAGE" or catogory=="FUNERAL" or catogory=="ANNUAL" or catogory=="OFFICIAL" or catogory=="INJURY":
        rate = 0
    elif catogory == "PERSONAL" or (catogory == "OTHERS"):
        rate = 1
    else:
        rate = 1
    return rate

#test case
#print (find_labor(80000), find_health(80000), find_retirement(80000))
#print (convert_labor(find_labor(80000)), convert_health(find_health(80000)), convert_retirement(find_retirement(80000)))
#print (get_annual(1997,7,17))
#print(get_hour(2021,7,17,8,11,2021,7,17,17,00))
#print(int(4.83))