# for moving to simpler member-contact relationships -- no more m2m

import os
import sys
from django.core.management import setup_environ

MESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, MESS_DIR)
import settings
setup_environ(settings)

from membership import models 

members = models.Member.objects.all()

#for member in members:
#    print "Reconnecting for %s ..." % member,
#    for address in member.addresses.all():
#        print "%s" % address,
#        address.member = member
#        address.save()
#    for phone in member.phones.all():
#        print "%s" % phone,
#        phone.member = member
#        phone.save()
#    for email in member.emails.all():
#        print "%s" % email,
#        email.member = member
#        email.save()
#    print

for member in members:
    print "Clearing contacts for %s ..." % member
    member.addresses.clear()
    member.emails.clear()
    member.phones.clear()
