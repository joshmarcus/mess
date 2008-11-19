# for moving to a "through" m2m for members and accounts

# add parent directory to the path
from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import settings

from django.core.management import setup_environ
setup_environ(settings)

from membership import models 

accounts = models.Account.objects.all()

for account in accounts:
    print "Processing %s ..." % account,
    for member in account.members.all():
        account_contact = account.contact == member
        primary_account = member.primary_account == account
        account_member = models.AccountMember(
            account=account,
            member=member, 
            account_contact=account_contact,
            primary_account=primary_account,
        )
        account_member.save()
    print "done."

