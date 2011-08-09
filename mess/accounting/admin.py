from django.contrib import admin
from mess.accounting import models


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'account', 'member', 'purchase_amount', 'purchase_type', 'payment_amount', 'payment_type', 'account_balance')
    ordering = ('-timestamp', '-id')
    search_fields = ('account__name', 'member__user__username')

admin.site.register(models.Transaction, TransactionAdmin)
