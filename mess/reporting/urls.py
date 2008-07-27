from datetime import date, timedelta
from django.conf.urls.defaults import *

date_today = date.today()
date_yesterday = date_today - timedelta(days=1)
date_tomorrow = date_today + timedelta(days=1)
dict_summary_today = {'start_date': date_today,
                    'end_date': date_tomorrow,
}
dict_summary_yesterday = {'start_date': date_yesterday,
                    'end_date': date_today,
}

urlpatterns = patterns('mess.reporting.views',
    url(r'^trans_summary/$', 'transaction_report', name='trans_summary'),
    url(r'^trans_summary_today/$', 'transaction_report', dict_summary_today,
                            name='trans_summary_today',),
    url(r'^trans_summary_yesterday/$', 'transaction_report', dict_summary_yesterday,
                            name='trans_summary_yesterday',),
)
