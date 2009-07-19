from datetime import date

from django.db import models
from django.core import exceptions
from django.contrib.auth.models import User

from mess.settings import LOCATION
from mess.membership.models import Account, Member

PURCHASE_CHOICES = (
    ('P','Purchase'),
    ('B','Bulk Purchase'),
    ('A','After-Hours Purchase'),
    ('U','Dues'),
    ('O','Deposit'),
#   ('S','Misc Sales'),   what is Misc Sales?
#   ('T','Trade'),    what is Trade?
    ('X','Correction'),
)

PAYMENT_CHOICES = (
    ('C','Credit Card'),
    ('D','Debit Card'),
    ('K','Check'),
    ('M','Money Order'),
    ('E','EBT'),
    ('W','Work Credit'),
    ('X','Correction'),
)

class Transaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    purchase_type = models.CharField(max_length=1, choices=PURCHASE_CHOICES,
        blank=True, default='P')
    purchase_amount = models.DecimalField(max_digits=5, decimal_places=2, 
        default=0, blank=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_CHOICES,
        blank=True)
    payment_amount = models.DecimalField(max_digits=5, decimal_places=2, 
        default=0, blank=True)
    note = models.CharField(max_length=256, blank=True)
    account_balance = models.DecimalField(max_digits=5, decimal_places=2)
    # reference is for check numbers, etc.  will uncomment when necessary
    #reference = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return str(self.date)

    def save(self, force_insert=False, force_update=False):
        balance = self.account.balance
        new_balance = balance + self.purchase_amount - self.payment_amount
        self.account.balance = self.account_balance = new_balance
        self.account.save()
        super(Transaction, self).save(force_insert, force_update)

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
        return str(self.date)

