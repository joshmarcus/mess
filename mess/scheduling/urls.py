from django.conf.urls.defaults import *

# commented out until there are actual views to point at -- 
# phantom urls wreak havoc with {% url %} and reverse()
urlpatterns = patterns('mess.scheduling.views',
    url(r'^monthly/(?P<month>.*)', 'monthly', name="staff-schedules"),
#    url(r'^weekly.html', 'weekly'),
#    url(r'^daily.html', 'daily'),
#    url(r'^job_list.html', 'job_list'),
)