from attendance.models import Leave, Daily, Overtime, Total, User, Total_leave
from django.contrib import admin

# Register your models here.
admin.site.register(User)
admin.site.register(Leave)
admin.site.register(Overtime)
admin.site.register(Daily)
admin.site.register(Total_leave)
admin.site.register(Total)
