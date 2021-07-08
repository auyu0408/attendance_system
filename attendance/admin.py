from attendance.models import Edited, Leave_form, Origin, Total, User
from django.contrib import admin

# Register your models here.
admin.site.register(User)
admin.site.register(Leave_form)
admin.site.register(Origin)
admin.site.register(Edited)
admin.site.register(Total)
