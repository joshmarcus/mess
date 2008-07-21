from django.conf.urls.defaults import *
from mess.membership.models import Member, Account

urlpatterns = patterns('mess.membership.views',
    (r'^monthly.html', 'Monthly'),
    (r'^weekly.html', 'Weekly'),
    (r'^daily.html', 'Daily'),
    (r'^job_list.html', 'Job List'),
)