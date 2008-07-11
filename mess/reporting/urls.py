from django.conf.urls.defaults import *

urlpatterns = patterns('mess.reporting.views',
    url(r'^daily_report$', 'daily_report', name='daily_report'),
)
