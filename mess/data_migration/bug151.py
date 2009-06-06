#!/usr/bin/python

# This script is intended to move from a member.status flag to 
# departed_date, missing_date, and leave of absense table.
# 
import pdb

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# can't be imported until we run setup_environ
from mess.membership import models
import datetime

# query to grab all members.
allmembers = models.Member.objects.all()
for mem in allmembers:
    if mem.status == 'd':
        mem.date_departed = datetime.date(1950,1,1)
    elif mem.status in 'mx': 
        mem.date_missing = datetime.date(1950,1,1)
    elif mem.status == 'L':
        LOA = models.LeaveOfAbsence(member=mem, start=datetime.date(1950,1,1), end=datetime.date(2050,1,1))
        LOA.save()
    mem.save()
    print "member %s status was %s." % (mem.user.username, mem.status)



