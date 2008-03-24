from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    (r'^thanks$','thanks'),
    (r'^transaction$', 'transaction_form'),
    (r'^member_transaction$', 'member_transaction'),
    (r'^staff_transaction$', 'staff_transaction'),
    (r'^cashier$', 'cashier'),
    #(r'^get_accounts/(d{0,10})$', 'get_accounts'),
)
