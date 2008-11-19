from django.contrib import admin

from mess.membership import models


class AddressInline(admin.TabularInline):
    model = models.Address

class EmailInline(admin.TabularInline):
    model = models.Email

class PhoneInline(admin.TabularInline):
    model = models.Phone

class MemberAdmin(admin.ModelAdmin):
    inlines = (
        AddressInline,
        EmailInline,
        PhoneInline,
    )

class AccountAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.AccountMember)
admin.site.register(models.Address)
admin.site.register(models.Email)
admin.site.register(models.Phone)
