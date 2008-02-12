from django.db import models

from mess.membership.models import Account, Member

TRANSACTION_TYPES = (
    ('p', 'Purchase'),
    ('c', 'Cash'),
    ('h', 'Check'),
    ('r', 'Credit Card'),
    ('d', 'Debit Card'),
)
class Transaction(models.Model):
    type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.TextField()
    ref = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.date
    
    class Admin:
        pass

class Reconciliation(models.Model):
    # reconciled_by provides a record of who did the reconciling, and could 
    # relate to Member or User, and overlaps with 
    # django.contrib.admin.LogEntry, should we choose to use that as a 
    # record keeper (would need to add LogEntry.objects.log_action() to this 
    # class's save() method).
    reconciled_by = models.ForeignKey(Member)
    transaction = models.ForeignKey(Transaction)
    reconciled = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.date
    
    class Admin:
        pass
