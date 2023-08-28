from django.contrib import admin
from . models import Profile, Attendance, Leave, Workday

# Register your models here.
admin.site.register(Profile)
admin.site.register(Attendance)
admin.site.register(Leave)
admin.site.register(Workday)
