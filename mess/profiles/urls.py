from django.conf.urls.defaults import *

urlpatterns = patterns('mess.profiles.views',
    url(r'^(\w+)/add_(\w+)/$', 'add_contact', name='add_contact'),
    url(r'^(\w+)/remove_contact/$', 'remove_contact', name='remove_contact'),
)

