from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models
import datetime

for account in models.Account.objects.all():
    booked_deposit = account.deposit
    logged_deposit = 0
    most_recent_timestamp = None
    most_recent_amount = None
    deposit_transactions = account.transaction_set.filter(purchase_type='O')
    for t in deposit_transactions:
        logged_deposit += t.purchase_amount
        most_recent_timestamp = t.timestamp
        most_recent_amount = t.purchase_amount
    if booked_deposit == logged_deposit:
        matches = 'matches'
    else:
        matches = 'does not match'
        if sys.argv[-1] == '-yes' and datetime(2010,10,24) < most_recent_timestamp < datetime(2010,10,25) and most_recent_amount == 20:
            account.deposit = logged_deposit
            account.save()
            matches = 'now updated to match'
    print 'Booked Deposit %3s %s Logged Deposit %3s, most recently logged %3s on %s, Account %s' % (
        booked_deposit, matches, logged_deposit, most_recent_amount, most_recent_timestamp, repr(account.name))
    

