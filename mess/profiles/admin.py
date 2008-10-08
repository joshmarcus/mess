from django.contrib import admin
from mess.profiles import models

class UserProfileAdmin(admin.ModelAdmin):
    pass

class AddressAdmin(admin.ModelAdmin):
    search_fields = ['address1', 'address2']

class PhoneAdmin(admin.ModelAdmin):
    pass

class EmailAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.Phone, PhoneAdmin)
admin.site.register(models.Email, EmailAdmin)
