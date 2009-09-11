'''
10 sept 2009
for clean up of mess due to creating tasks but failing to save their recur_rule.
'''

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.scheduling import models
import datetime

sentinels = models.Task.objects.filter(time__gt=datetime.date(2010,12,1), recur_rule__isnull=True)

knownids={}

for sentinel in sentinels:
    if sentinel.id in knownids:
        contine
    walkback = sentinel.id
    while models.Task.objects.get(id=walkback).recur_rule is None:
        walkback -= 1

    walkforward = sentinel.id
    try:
        while models.Task.objects.get(id=walkforward).time >= sentinel.time:
            walkforward += 1
    except:
        pass

    for id in range(walkback, walkforward):
        t = models.Task.objects.get(id=id)
        knownids[id] = t
        print 'Task', id, t, t.recur_rule
    print '-------'

