from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from mess.membership import models

for m in models.Member.objects.all():
    print repr('\t'.join((m.user.username, m.user.first_name, m.user.last_name, m.get_primary_account().name, m.user.email, (';'.join(str(e) for e in m.emails.all())))))
