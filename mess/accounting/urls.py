from django.conf.urls.defaults import *

urlpatterns = patterns('mess.accounting.views',
    (r'^thanks$','thanks'),
    url(r'^transaction/$', 'transaction_form', name='transaction'),
    url(r'^cashier$', 'cashier', name='cashier'),
    url(r'^close_out/$', 'close_out', name='close_out'),
    
    url(r'^close_out/checks/$', 'close_out',
        {'type': 'K'}, name='close_out_checks' ),
    url(r'^close_out/money_orders/$', 'close_out', 
        {'type': 'M'}, name='close_out_money_orders'),
    url(r'^close_out/credit/$', 'close_out',
        {'type': 'C'}, name='close_out_credit'),
    url(r'^close_out/ebt/$', 'close_out',
        {'type': 'F'}, name='close_out_ebt'),
    url(r'^close_out/all/$', 'close_out', name='close_out'),
    
    #(r'^get_accounts/(d{0,10})$', 'get_accounts'),
)
