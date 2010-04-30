from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models

for m in models.Member.objects.all():
    e = m.emails.all()
    if e:
        u = m.user
        u.email = e[0].email
        u.save()

