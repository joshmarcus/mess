from django.contrib import admin
from mess.scheduling import models

class TaskExcludeTimeInline(admin.TabularInline):
    model = models.TaskExcludeTime

class TaskAdmin(admin.ModelAdmin):
    list_display = ('job', 'time', 'hours', 'deadline', 'member', 'account',
            'frequency', 'interval')
    list_filter = ('deadline', )
    inlines = (
        TaskExcludeTimeInline,
    )

admin.site.register(models.Job)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.Timecard)
admin.site.register(models.Skill)
