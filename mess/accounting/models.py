from datetime import date

from django.db import models
from django.db.transaction import commit_on_success
from django.core import exceptions
from django.contrib.auth.models import User

from mess.settings import LOCATION
from mess.membership.models import Account, Member
from mess.membership import models as m_models

PURCHASE_CHOICES = (
    ('P','Purchase'),
    ('B','Bulk Purchase'),
    ('A','After-Hours Purchase'),
    ('U','Dues'),
    ('O','Member Equity'),
    ('G','Gift or Loan'),
    ('S','Misc'),   # Misc is used for transfers etc, positive or negative
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

class HoursTransaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account)
    hours_balance_change = models.DecimalField(max_digits=5, decimal_places=2,
        default=0, blank=True)
    note = models.CharField(max_length=256, blank=True)
    hours_balance = models.DecimalField(max_digits=5, decimal_places=2)
    entered_by = models.ForeignKey(User, blank=True, null=True)

    def save(self, force_insert=False, force_update=False):
        old_balance = self.account.hours_balance
        new_balance = old_balance + self.hours_balance_change
        self.account.hours_balance = self.hours_balance = new_balance
        self.account.save()
        super(HoursTransaction, self).save(force_insert, force_update)

class Transaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True) #never have to deal w/ this in a form.
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member, blank=True, null=True)
    purchase_type = models.CharField(max_length=1, choices=PURCHASE_CHOICES,
        blank=True, default='P')
    purchase_amount = models.DecimalField(max_digits=8, decimal_places=2, 
        default=0, blank=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_CHOICES,
        blank=True)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, 
        default=0, blank=True)
    note = models.CharField(max_length=256, blank=True)
    account_balance = models.DecimalField(max_digits=8, decimal_places=2)
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
        if self.purchase_type == 'O':  # Member Equity
            self.account.deposit += self.purchase_amount
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
            return [] # transaction was not a correction.

    def fixers(self):
        if self.note and self.note[0] == '@':
            return []  # disregard recursive fixers
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
        ebtbo = self.ebtbulkorder_set.all()
        if ebtbo:
            for order in ebtbo:
                # do nothing.  trying to reduplicate the reversed EBT b.o.s
                # just creates more confusion.
                #order.duplicate_after_reversed()
                pass
        rev = Transaction(account=self.account,
                          member=self.member,
                          purchase_type=self.purchase_type,
                          purchase_amount= -self.fixed_purchase_amount(),
                          payment_type=self.payment_type,
                          payment_amount= -self.fixed_payment_amount(),
                          note='@%s reversed: %s' % (self.id, reason),
                          entered_by=entered_by)        
        rev.save()

    def note_plus_spaces(self):
        return self.note.replace('+',' + ')

    class Meta:
        ordering = ['timestamp']
        

class EBTBulkOrderManager(models.Manager):
    def unpaid(self):
        return self.filter(paid_by_transaction__isnull=True, amount__gt=0)
    def paid(self):
        return self.exclude(paid_by_transaction__isnull=True, amount__gt=0)

class EBTBulkOrder(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account)
    amount = models.DecimalField(max_digits=8, decimal_places=2,
        default=0, blank=True)
    paid_by_transaction = models.ForeignKey(Transaction, null=True)
    note = models.CharField(max_length=256, blank=True)

    objects = EBTBulkOrderManager()

    def __unicode__(self):
        return '%s EBT bulk ordered %s on %s' % (self.account, 
                self.amount, self.order_date)

    def duplicate_after_reversed(self):
        """ this is called when the order was already paid, but then
        the transaction was reversed.  we create a duplicate of the original
        EBT bulk order. """
        duplicate = EBTBulkOrder(order_date=self.order_date,
                account=self.account,
                amount=self.amount,
                note='(reversed) '+self.note)
        duplicate.save()

    def save(self, force_insert=False, force_update=False):
        if self.id:
            oldself = EBTBulkOrder.objects.get(id=self.id)
            if oldself.paid_by_transaction:
                raise AssertionError, "cannot edit EBT bulk order already paid"
        super(EBTBulkOrder, self).save(force_insert, force_update)


class StoreDay(models.Model):
    # timepoints when the store is 'opened' for the next day's business.
    # transactions naturally divide into days, according to these breakpoints.
    # so for example, Friday early-morning corrections count as part of 
    # Thursday's store day
    start = models.DateTimeField()

    def get_end(self):
        later = StoreDay.objects.filter(start__gt=self.start)
        if later:
            return later[0].start
    #end = property(get_end)

    class Meta:
        ordering = ['start']

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

def total_balances_on(time):
    ''' I want to do something more like...
        select sum(account_balance) from accounting_transaction t
        where t.timestamp < %s
        and not exists (
            select 1 from accounting_transaction
            where account_id=t.account_id and timestamp > t.timestamp
            and timestamp < %s )
        But I can't figure how to translate that kind of SQL into Django...
    '''
    total = 0
    for account in m_models.Account.objects.all():
        total += account.balance_on(time) or 0
    return total

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

