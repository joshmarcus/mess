from django.db import models
from django.core import exceptions

from mess.membership.models import Account, Member

# Is it better to have these lists in the model or out?

# Credit is looked at from the stores point of view.  A credit
# will be a positive number.

COMMON_CREDIT_CHOICES = (
    ('N','None'),
)

MEMBER_CREDIT_CHOICES = (
    ('E','Extras'),
)

CASHIER_CREDIT_CHOICES = (
    ('P','Purchase'),
)

OTHER_CREDIT_CHOICES = (
    ('B','Bulk Purchase'),
    ('U','Dues'),
    ('S','Misc Sales'),
)

# A debit is looked at from the stores point of view.  A debit
# will be a negative number.
COMMON_DEBIT_CHOICES = (
    ('N','None'),
)

CASHIER_DEBIT_CHOICES = (
    ('C','Credit Card'),
    ('D','Debit Card'),
    ('K','Check'),
    ('M','Money Order'),
    ('E','EBT'),
)

OTHER_DEBIT_CHOICES = (
    ('W','Work Credit'),
    ('T','Trade'),
    ('H','Deposit'),
    ('Y','Key Deposit'),
    ('X','Misc Debit'),
)

CREDIT_CHOICES = (COMMON_CREDIT_CHOICES + MEMBER_CREDIT_CHOICES +
                CASHIER_CREDIT_CHOICES + OTHER_CREDIT_CHOICES
                )

DEBIT_CHOICES = (COMMON_DEBIT_CHOICES + CASHIER_DEBIT_CHOICES +
                OTHER_DEBIT_CHOICES
                )

def get_account_balance(id):
    try:
        return Transaction.objects.filter(member=id).latest('date').balance
    except exceptions.ObjectDoesNotExist:
        return 0

def get_account_transactions(id):
    return Transaction.objects.filter(member=id)


class Transaction(models.Model):
    credit_type = models.CharField(max_length=1, choices=CREDIT_CHOICES,
                                    default='N',)
    debit_type = models.CharField(max_length=1, choices=DEBIT_CHOICES,
                                    default='N',)
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    # I think having a debit and credit field will make calculations easier.
    # It is also more in line with other accounting applications.
    #
    # The question is how exactly to use it.  If the transaction is a 
    # 'Key Deposit' which is a debit as far as the coop is concerned,
    # it would go in the debit field.
    #
    # If the transaction is to return a 'Key Deposit', say a refund of $10.00
    # does it go in debit as -10.00 or credit.  Okay so I my example may not
    # be accurate but I hope it illustrates what I mean.
    credit = models.DecimalField(max_digits=5, decimal_places=2, default=0,)
    debit = models.DecimalField(max_digits=5, decimal_places=2, default=0,)
    #  If each Transaction has the account balance we probably don't need this.
    balance = models.DecimalField(max_digits=5, decimal_places=2, blank=True,
                                    verbose_name="Account Balance")
    # Changed this to CharField. Is there a reason for a TextField here?
    note = models.CharField(max_length=100, blank=True)
    ref = models.PositiveIntegerField(blank=True, null=True,
                                        verbose_name='Reference')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.date)

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
