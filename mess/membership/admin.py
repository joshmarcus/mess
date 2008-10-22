from django.contrib import admin

from mess.membership import models


class MemberAdmin(admin.ModelAdmin):
    pass


class AccountAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Address)
admin.site.register(models.Email)
admin.site.register(models.Phone)
