from datetime import date

from django.db import models
from django.db.transaction import commit_on_success
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
    ('S','Misc Sales'),   # what is Misc Sales?  it's on the cash sheets...
#   ('T','Trade'),    what is Trade?
)

PAYMENT_CHOICES = (
    ('C','Credit Card'),
    ('D','Debit Card'),
    ('K','Check'),
    ('M','Money Order'),
    ('E','EBT'),
    ('W','Work Credit'),
)

class Transaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member, blank=True, null=True)
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
    entered_by = models.ForeignKey(User, blank=True, null=True)
    # reference is for check numbers, etc.  will uncomment when necessary
    #reference = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return '%s %s' % (self.account, 
                          self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    def save(self, force_insert=False, force_update=False):
        # purchase_amount and purchase_type must appear together
        if bool(self.purchase_amount) is not bool(self.purchase_type):
            self.purchase_amount = 0
            self.purchase_type = ''
        if bool(self.payment_amount) is not bool(self.payment_type):
            self.payment_amount = 0
            self.payment_type = ''
        balance = self.account.balance
        new_balance = balance + self.purchase_amount - self.payment_amount
        self.account.balance = self.account_balance = new_balance
        self.account.save()
        super(Transaction, self).save(force_insert, force_update)

    def fixes_target(self):
        '''
        If this transaction is a correction, returns the target of the fix.
        Determined based on note starting with "@id "
        '''
        try:
            if self.note[0] == '@':
                target_id = self.note.split()[0][1:]
                target = Transaction.objects.get(id=target_id)
                if target.note and target.note[0] == '@':
                    return None  # disregard recursive fixers
                return target
        except:
            return None

    def fixers(self):
        if self.note and self.note[0] == '@':
            return None  # disregard recursive fixers
        return Transaction.objects.filter(note__startswith='@%s ' % self.id)
        
    def fixed_payment_amount(self):
        payment = self.payment_amount
        for fixer in self.fixers():
            payment += fixer.payment_amount
        return payment

    def fixed_purchase_amount(self):
        purchase = self.purchase_amount
        for fixer in self.fixers():
            purchase += fixer.purchase_amount
        return purchase

    def reverse(self, entered_by, reason=''):
        rev = Transaction(account=self.account,
                          member=self.member,
                          payment_type=self.payment_type,
                          payment_amount= -self.fixed_payment_amount(),
                          purchase_type=self.purchase_type,
                          purchase_amount= -self.fixed_purchase_amount(),
                          note='@%s reversed: %s' % (self.id, reason),
                          entered_by=entered_by)        
        rev.save()

    def fix_payment(self, entered_by, fix_payment):
        keep_purchase_amount = self.fixed_purchase_amount()
        self.reverse(entered_by=entered_by, reason='to fix payment')
        fix = Transaction(account=self.account,
                          member=self.member,
                          payment_type=self.payment_type,
                          payment_amount=fix_payment,
                          purchase_type=self.purchase_type,
                          purchase_amount=keep_purchase_amount,
                          note='@%s fixed payment' % self.id,
                          entered_by=entered_by)
        fix.save()
        

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

@commit_on_success
def commit_potential_bills(accounts, bill_type, entered_by):
    for account in accounts:
        bill = Transaction(account=account,
                           purchase_type=bill_type,
                           purchase_amount=account.potential_bill,
                           entered_by=entered_by)
        bill.save()
        if bill_type == 'O': #deposit
            account.deposit += account.potential_bill
            account.save()

