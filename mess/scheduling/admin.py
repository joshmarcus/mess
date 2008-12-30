from django.contrib import admin
from mess.scheduling import models

class ExclusionInline(admin.TabularInline):
    model = models.Exclusion

class TaskInline(admin.TabularInline):
    model = models.Task

class RecurRuleAdmin(admin.ModelAdmin):
    model = models.RecurRule
    inlines = (
        ExclusionInline,
        TaskInline,
    )

class TaskAdmin(admin.ModelAdmin):
    list_display = ('job', 'time', 'hours')
    list_filter = ('job', )

admin.site.register(models.Job)
admin.site.register(models.RecurRule, RecurRuleAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.Timecard)
admin.site.register(models.Skill)
admin.site.register(models.Worker)
