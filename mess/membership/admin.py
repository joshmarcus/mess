from django.contrib import admin
from mess.membership.models import Member, Account

class MemberAdmin(admin.ModelAdmin):
    pass
class AccountAdmin(admin.ModelAdmin):
    pass
admin.site.register(Member, MemberAdmin)
admin.site.register(Account, AccountAdmin)
