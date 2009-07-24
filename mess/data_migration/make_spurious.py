import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# these imports raise errors if placed before setup_environ(settings)
from mess.membership import models as m_models
from mess.accounting import models as a_models
import random
from decimal import Decimal

accts = m_models.Account.objects.active()
for x in range(10):
    t = a_models.Transaction(account=random.choice(accts),
          purchase_type=random.choice('PPPAB'), 
          purchase_amount=random.randrange(50)/Decimal(4),
          payment_type=random.choice(['C','D','K','M','E','','','','','']),
          payment_amount=random.randrange(90)/Decimal(4))
    t.save()
