from django.contrib import admin
from mess.events import models

admin.site.register(models.Location)
admin.site.register(models.Orientation)
