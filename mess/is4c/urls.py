from django.conf.urls.defaults import *

urlpatterns = patterns('mess.is4c.views',
    url(r'^$', 'index', name='is4c-index'),
    url(r'^account/(\d+)/$', 'account', name='is4c-account'),
    url(r'^accounts/$', 'accounts', name='is4c-accounts'),
    url(r'^member/(\d+)/$', 'member', name='is4c-member'),
    url(r'^members/$', 'members', name='is4c-members'),
    url(r'^recordtransaction/$', 'recordtransaction', name='is4c-recordtransaction'),
)
