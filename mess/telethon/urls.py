from django.conf.urls.defaults import *

urlpatterns = patterns('mess.telethon.views',
    url(r'^$', 'index', name='telethon-index'),
    url(r'^(\w+)$', 'member', name='telethon-member'),
)
