from django.conf.urls.defaults import *

urlpatterns = patterns('mess.reporting.views',
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^list/$', 'list', name='list'),
    url(r'^anomalies/$', 'anomalies', name='anomalies'),
    url(r'^memberwork/$', 'memberwork', name='memberwork'),

    # everything below here is partly unused or deprecated
    url(r'^contact/$', 'contact', name='contact_list'),
    url(r'^trans_summary/$', 'transaction_report',
                            {'report': 'all'}, name='trans_summary'),
    url(r'^trans_summary_today/$', 'transaction_report',
                            {'report': 'today'}, name='trans_summary_today',),
    url(r'^trans_summary_yesterday/$', 'transaction_report',
                            {'report': 'yesterday'},
                            name='trans_summary_yesterday',),
    url(r'^trans_summary_week/$', 'transaction_report',
                            {'report': 'week'}, name='trans_summary_week',),
    url(r'^trans_summary_month/$', 'transaction_report',
                            {'report': 'month'}, name='trans_summary_month'),
    url(r'^trans_summary_year/$', 'transaction_report',
                            {'report': 'year'}, name='trans_summary_year'),
    url(r'^trans_summary_custom/$', 'transaction_report',
                            {'report': 'custom'}, name='trans_summary_custom'),
    url(r'^trans_list/$', 'transaction_list_report', name='trans_list'),
)
