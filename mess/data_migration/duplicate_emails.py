from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models

all_the_emails = []
for m in models.Member.objects.all():
    if not m.user.email: continue
    if m.user.email in all_the_emails:
        print m.user.email,
        for d in models.Member.objects.filter(user__email=m.user.email):
            print d.user.username,
        print
    else:
        all_the_emails.append(m.user.email)
    #e = m.emails.all()
    #if e and unicode(e[0]) != unicode(m.user.email):
    #    count += 1
    #    print count,
    #    print m.id,
    #    print m.user.username,
    #    print e[0],
    #    print m.user.email
    #if e:
    #    u = m.user
    #    u.email = e[0].email
    #    u.save()
