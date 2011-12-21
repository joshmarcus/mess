from os.path import dirname, abspath
import datetime
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models
from mess.accounting import models as a_models
accts = models.Account.objects.all()
entered_by = models.Member.objects.get(user__id=1007).user # anna
total = 0
for acct in accts:
    if acct.members.count() == 1 and acct.deposit != 0:
        if acct.members.get().date_departed==datetime.date(1904,1,1):
            total += 1
            print "Before Transfer: " + repr(acct.name), acct.deposit, repr(acct.members.get()), acct.members.get().equity_held
            old_deposit = acct.deposit
            trans1 = a_models.Transaction(
                            note='transferring equity from account',
                            account=acct,
                            entered_by=entered_by, purchase_type='O',
                            purchase_amount=-old_deposit)
            trans1.save_for_equity_transfer()
            trans2 = a_models.Transaction(
                            note='transferring equity to member',
                            account=acct,
                            member=acct.members.get(),
                            entered_by=entered_by, purchase_type='O',
                            purchase_amount=old_deposit)
            trans2.save_for_equity_transfer()
            print "     After Transfer: " + repr(acct.name), acct.deposit, repr(acct.members.get()), acct.members.get().equity_held
print total, "equities transferred"
