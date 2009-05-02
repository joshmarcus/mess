#!/usr/bin/python

# This is a one-off script to fix Excel Dates that were put into MESS
# as strings like "41590.0" instead of being converted to dates by xlrd.

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

import xlrd
import datetime
import re
from django.db import transaction
from mess.membership import models

# these imports raise errors if placed before setup_environ(settings)
#import string
#import time
#from random import choice
#from django.shortcuts import get_object_or_404
#from django.contrib.auth.models import User
#from django.db import IntegrityError
#from mess.scheduling import models as s_models

def fixdate(baddate):
    date = xlrd.xldate_as_tuple(float(baddate),0)
    return '%s/%s/%s' % (date[1], date[2], date[0])

@transaction.commit_on_success
def fixdates():
    baddateseeker = re.compile(r'[34][0-9][0-9][0-9][0-9]\.0')
    for acct in models.Account.objects.all():
        print repr('Account: %s' % acct.name)
        baddate = baddateseeker.search(acct.note)
        while baddate:
            acct.note = acct.note[:baddate.start()] + fixdate(baddate.group()) \
                        + acct.note[baddate.end():]
            acct.save()
            print 'Converted %s to %s.' % (baddate.group(), fixdate(baddate.group()))
            baddate = baddateseeker.search(acct.note)

fixdates()

