from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    (r'^thanks$','thanks'),
    url(r'^transaction$', 'transaction_form', name='transaction'),
    #(r'^member_transaction$', 'member_transaction'),
    #(r'^staff_transaction$', 'staff_transaction'),
    url(r'^cashier$', 'cashier', name='cashier'),
    url(r'^close_out', 'close_out', name='close_out'),
    #(r'^get_accounts/(d{0,10})$', 'get_accounts'),
)
