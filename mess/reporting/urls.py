from django.conf.urls.defaults import *

urlpatterns = patterns('mess.reporting.views',
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^list/$', 'list', name='list'),
    url(r'^equity/$', 'equity', name='equity'),
    url(r'^equity_transfer/$', 'equity_transfer', name='equity_transfer'),
    url(r'^equity_old/$', 'equity_old', name='equity_old'),
    url(r'^anomalies/$', 'anomalies', name='anomalies'),
    url(r'^memberwork/$', 'memberwork', name='memberwork'),
    url(r'^trans_summary/$', 'trans_summary', name='trans_summary'),
    url(r'^hours_balance_changes/$', 'hours_balance_changes', name='hours_balance_changes'),
    url(r'^turnout/$', 'turnout', name='turnout'),

    # everything below here is partly unused or deprecated
    url(r'^contact/$', 'contact', name='contact_list'),
    url(r'^trans_list/$', 'transaction_list_report', name='trans_list'),
)
