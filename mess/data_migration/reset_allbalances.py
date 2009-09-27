# Resets all account balances and deposits to 0, and deletes all transactions
# Used before migrating accounting data into MESS.
# commit_on_success, so if user stops it with Ctrl-C, everything is preserved

from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.db import transaction
from mess.membership import models
from mess.accounting import models as a_models

@transaction.commit_on_success
def main():
    print 'Resetting all account balances to 0'
    print 'to cancel and not reset anything, press Ctrl-C NOW'
    accounts = models.Account.objects.all()
    for account in accounts:
        account.balance = 0
        account.deposit = 0
        account.save()

    print 'Deleting all transaction history'
    transactions = a_models.Transaction.objects.all()
    for transaction in transactions:
        transaction.delete()

main()
