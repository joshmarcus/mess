from django.conf.urls.defaults import *

urlpatterns = patterns('mess.core.views',
    url(r'^$', 'welcome', name='welcome'),
)
