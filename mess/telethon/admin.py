from django.contrib import admin
from mess.telethon import models

class CallAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Call, CallAdmin)

