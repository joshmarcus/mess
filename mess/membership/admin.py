from django.contrib import admin
from mess.membership.models import Member

class MemberAdmin(admin.ModelAdmin):
    pass
admin.site.register(Member, MemberAdmin)
