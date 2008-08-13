from django.contrib import admin
from mess.scheduling.models import Job, Task, Timecard

admin.site.register(Job)
admin.site.register(Task)
admin.site.register(Timecard)
