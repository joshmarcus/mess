from django.conf.urls.defaults import *

urlpatterns = patterns('mess.profiles.views',
    url(r'^(\w+)/add_phone/$', 'add_phone', name='add_phone'),
    url(r'^(\w+)/remove_phone/$', 'remove_phone', name='remove_phone'),
)

