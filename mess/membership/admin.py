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
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

class AccountAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class AccountMemberAdmin(admin.ModelAdmin):
    search_fields = ('account__name', 'member__user__username')


admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.AccountMember, AccountMemberAdmin)
admin.site.register(models.Address)
admin.site.register(models.Email)
admin.site.register(models.Phone)
admin.site.register(models.MemberSignUp)
