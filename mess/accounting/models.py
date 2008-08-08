from datetime import date

from django.db import models
from django.core import exceptions
from django.contrib.auth.models import User

from mess.settings import LOCATION
from mess.membership.models import Account, Member

# Is it better to have these lists in the model or out?

# Credit is looked at from the store's point of view.  A credit
# will be a positive number.

NO_CREDIT_CHOICES = (
    ('N', None),
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
    ('T','Trade'),
    ('W','Work Credit'),
)

# A debit is looked at from the stores point of view.  A debit
# will be a negative number.
NO_DEBIT_CHOICES = (
    ('N', None),
)

CASHIER_DEBIT_CHOICES = (
    ('C','Credit Card'),
    ('D','Debit Card'),
    ('K','Check'),
    ('M','Money Order'),
    ('F','EBT'),
)

OTHER_DEBIT_CHOICES = (
    #('W','Work Credit'),
    #('T','Trade'),
    ('H','Deposit'),
    ('Y','Key Deposit'),
    ('X','Misc Debit'),
)

def get_credit_choices(role=None, location=None):
    try:
        location = LOCATION
    except:
        pass
    # This logic needs work-dv
    if role == None and location == None:
        return NO_CREDIT_CHOICES
    elif role == 'Member':
        return NO_CREDIT_CHOICES + MEMBER_CREDIT_CHOICES
    elif role == 'Cashier' and location == 'Cashier':
        return NO_CREDIT_CHOICES + CASHIER_CREDIT_CHOICES
    elif role == 'Staff':
        return (NO_CREDIT_CHOICES + MEMBER_CREDIT_CHOICES +
                CASHIER_CREDIT_CHOICES + OTHER_CREDIT_CHOICES
                )

def get_debit_choices(role=None, location=None):
    # This logic needs work. - dv
    try:
        location = LOCATION
    except:
        pass
    if role == None and location == None:
        return NO_DEBIT_CHOICES
    elif role == 'Member' and location == None:
        return NO_DEBIT_CHOICES
    elif role == 'Cashier' and location == 'Cashier':
        return NO_DEBIT_CHOICES + CASHIER_DEBIT_CHOICES
    elif role == 'Staff':
        return (NO_DEBIT_CHOICES + CASHIER_DEBIT_CHOICES + OTHER_DEBIT_CHOICES)

def get_account_balance(id):
    try:
        return Transaction.objects.filter(member=id).latest('date').balance
    except exceptions.ObjectDoesNotExist:
        return 0

def get_account_transactions(id):
    return Transaction.objects.filter(member=id)

def get_todays_transactions():
    d = date.today()
    return Transaction.objects.filter(date__year = d.year,
                                        date__month = d.month,
                                        date__day = d.day)

def get_trans_total(trans, type='all'):
    total = 0
    if type == 'all' or type == 'debit':
        for tran in trans:
            total += tran.debit
    if type == 'all' or type == 'credit':
        for tran in trans:
            total += tran.credit
    return total

class Transaction(models.Model):
    credit_choices = get_credit_choices('Staff')
    debit_choices = get_debit_choices('Staff')

    credit_type = models.CharField(max_length=1, choices=credit_choices,
                                    default='N',)
    debit_type = models.CharField(max_length=1, choices=debit_choices,
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
	# 
	#    I like how you separate the debit and credit columns.  My opinion is
	#    if they're going to be separated, there should be no exceptions, so if
	#    a key deposit is $10 in one field, then a key deposit refund is $10
	#    in the other field.  i.e., no mixing +/- in one column. --Paul 8/3/08
	#
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
    reconciled_by = models.ForeignKey(User)
    transaction = models.ForeignKey(Transaction)
    reconciled = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.date)
    
    class Admin:
        pass
