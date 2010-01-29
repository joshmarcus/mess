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

def main():
    
    for t in a_models.Transaction.objects.filter(purchase_type='P'):
        try:
            a = t.account.active_members()[0].addresses.all()[0]
        except:
            try:
                a = m_models.Address.objects.filter(member__account=t.account)[0]
            except:
                # print "++++++++ %s" % t.account
                continue

        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (t.id, t.timestamp,
            a.address1, a.address2, a.city,
            a.state, a.postal_code, t.purchase_amount)
                
if __name__=='__main__':
    main()
