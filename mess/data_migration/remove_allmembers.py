# this is one way to remove fixtures before production.   you could say:

from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.db import transaction
from mess.membership import models

@transaction.commit_on_success
def main():
    print 'Removing all accounts...'
    accounts = models.Account.objects.all()

    # TODO should remove related objects like AccountMember_set
    for account in accounts:
        account.delete()

    print 'Removing all members except staff members...'
    members = models.Member.objects.filter(user__is_staff=False)

    # TODO should remove related objects like phones, emails, addresses
    for member in members:
        member.user.delete()
        member.delete()

main()
