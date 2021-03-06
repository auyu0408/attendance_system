# -*- coding: UTF-8 -*-
import datetime

from django.shortcuts import render
stander=[[0, 24000, 25200, 26400, 27600, 28800, 30300, 31800, 33300, 34800, 36300, 38200, 40100, 42000, 43900, 45800, 48200, 50600, 53000, 55400, 57800, 60800, 63800, 66800, 69800, 72800, 76500, 80200, 83900, 87600, 92100, 96600, 101100, 105600, 110100, 115500, 120900, 126300, 131700, 137100, 142500, 147900, 150000, 156400, 162800, 169200, 175600, 182000],
        [ 0, 552,   579,   607,   635,   663,   697,   732,   766,   801,   835,   878,   922,   966,   1010,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,  1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054,   1054],
        [ 0, 372,   391,   409,   428,   447,   470,   493,   516,   540,   563,   592,   622,   651,   681,   710,   748,   785,   822,   859,   896,   943,   990,   1036,  1083,  1129,  1187,  1244,  1301,  1359,  1428,  1498,  1568,   1638,   1708,   1791,   1875,   1959,   2043,   2126,   2210,   2294,   2327,   2426,   2525,   2624,   2724,   2823],
        [ 0, 1440,  1512,  1584,  1656,  1728,  1818,  1908,  1998,  2088,  2178,  2292,  2406,  2520,  2634,  2748,  2892,  3036,  3180,  3324,  3468,  3648,  3828,  4008,  4188,  4368,  4590,  4812,  5034,  5256,  5526,  5796,  6066,   6336,   6606,   6930,   7254,   7578,   7902,   8226,   8550,   8874,   9000,   9000,   9000,   9000,   9000,   9000]]
annual = [ 3, 7, 10, 14, 14, 15, 15, 15, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]


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

def get_seniority(year, month, day, year2, month2, day2):
    y = datetime.date(year2, month2, day2).year - datetime.date(year,month,day).year
    m = datetime.date(year2, month2, day2).month - datetime.date(year, month, day).month
    d = datetime.date(year2, month2, day2).day - datetime.date(year, month, day).day
    if d < 0:
        m -=1
    seniority = y + round(float(m)/12,2)
    return seniority

def get_annual(seniority):
    if seniority < 0.5:
        day = 0
    elif seniority < 25:
        day = annual[int(seniority)]
    else:
        day = 30
    return day

def get_day(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if ed < sd:
        return -1
    day = 0
    for date in range(sd, ed+1):
        if datetime.date(sy, sb, date).isoweekday() == 6 or datetime.date(sy, sb, date).isoweekday() == 7:
            pass
        else:
            day += 1
    day = day-2
    hour1 = get_hour(sy,sb,sd,sh,sm,sy,sb,sd,17,0)
    hour2 = get_hour(ey,eb,ed,8,0,ey,eb,ed,eh,em)
    if hour1 + 0.5 > int(hour1)+1:
        hour1 = int(hour1)+1
    elif hour1+0.5 > int(hour1)+0.5:
        hour1 = int(hour1)+0.5
    else:
        pass
    if hour2 + 0.5 > int(hour2)+1:
        hour2 = int(hour2)+1
    elif hour2+0.5 > int(hour2)+0.5:
        hour2 = int(hour2)+0.5
    else:
        pass
    day += round((hour1+hour2)/8,2)
    return day

def get_hour(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if sh == 12:
        sm = 0
    if eh == 12:
        em = 0
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    hour1 = round(float(day1.seconds)/3600,2)
    minute = (day1.seconds-hour1*3600)/60
    if sh <=12 and eh >12:
        hour1 = hour1 - 1
    hour = hour1 + day1.days*8
    return hour

def get_minute(sy,sb,sd,sh,sm,ey,eb,ed,eh,em):
    if sh == 12:
        sm = 0
    if eh == 12:
        em = 0
    day1 = datetime.datetime(ey,eb,ed,eh,em,0)-datetime.datetime(sy,sb,sd,sh,sm,0)
    minute = (day1.seconds)/60
    if sh <=12 and eh >12:
        minute -= 60
    return minute

def get_attend(sh,sm,eh,em):
    if sh == 12:
        sm = 0
    if eh == 12:
        em = 0
    if sh < 8:
        sh = 8
        sm = 0
    elif sh >= 17:
        sh = 17
        sm = 0
    else:
        pass
    if eh < 8:
        eh = 8
        em = 0
    elif eh >= 17:
        eh = 17
        em = 0
    else:
        pass
    day1 = datetime.datetime(2000,1,1,eh,em,0)-datetime.datetime(2000,1,1,sh,sm,0)
    hour1 = round(float(day1.seconds)/3600,2)
    minute = (day1.seconds-hour1*3600)/60
    if sh <=12 and eh >12:
        hour1 = hour1 - 1
    hour = hour1 + day1.days*8
    return hour

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

#test case
#print (find_labor(80000), find_health(80000), find_retirement(80000))
#print (convert_labor(find_labor(80000)), convert_health(find_health(80000)), convert_retirement(find_retirement(80000)))
#print (get_annual(1997,7,17))
#print(get_day(2021,7,25,8,0,2021,7,25,10,00))
#print(int(4.83))