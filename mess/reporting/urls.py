from django.conf.urls.defaults import *

urlpatterns = patterns('mess.reporting.views',
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^list/$', 'list', name='list'),
    url(r'^anomalies/$', 'anomalies', name='anomalies'),
    url(r'^memberwork/$', 'memberwork', name='memberwork'),
    url(r'^trans_summary/$', 'transaction_report', name='trans_summary'),

    # everything below here is partly unused or deprecated
    url(r'^contact/$', 'contact', name='contact_list'),
    url(r'^trans_list/$', 'transaction_list_report', name='trans_list'),
)
