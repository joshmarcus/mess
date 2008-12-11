from django.contrib import admin
from mess.scheduling import models

class TaskExcludeTimeInline(admin.TabularInline):
    model = models.TaskExcludeTime

class SubstituteInline(admin.TabularInline):
    model = models.Substitute

class TaskAdmin(admin.ModelAdmin):
    list_display = ('job', 'time', 'hours', 'frequency', 'interval')
    list_filter = ('job', )
    inlines = (
        TaskExcludeTimeInline,
        SubstituteInline,
    )

admin.site.register(models.Job)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.Timecard)
admin.site.register(models.Skill)
