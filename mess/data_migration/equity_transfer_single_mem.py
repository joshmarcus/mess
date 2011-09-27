'''
NOTE: DON'T RUN THIS YET!!!
Says Anna:
    This don't work 'cause:
        - trans1 subtracts account.deposit
        - so when trans2 tries to add it, it's zero.
    Doh.
'''
from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models
from mess.accounting import models as a_models
accts = models.Account.objects.all()
entered_by = models.Member.objects.get(user__id=259).user #This is Paul Dexter
for acct in accts:
    if acct.active_member_count == 1:
        print "Before Transfer: " + repr(acct.name), acct.deposit, repr(acct.members.active()[0]), acct.members.active()[0].equity_held
        trans1 = a_models.Transaction.objects.create(
                        note='transferring equity from account',
                        account=acct,
                        entered_by=entered_by, purchase_type='O',
                        purchase_amount=-acct.deposit)
        trans2 = a_models.Transaction.objects.create(
                        note='transferring equity to member',
                        account=acct,
                        member=acct.members.active()[0],
                        entered_by=entered_by, purchase_type='O',
                        purchase_amount=acct.deposit)
        print "After Transfer: " + repr(acct.name), acct.deposit, repr(acct.members.active()[0]), acct.members.active()[0].equity_held
