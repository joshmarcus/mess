from django.conf.urls.defaults import *

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts$', 'account_list', name='accounts'),
    url(r'^accounts/add$', 'account_form', name='account-add'),
    url(r'^accounts/(\d+)$', 'account', name='account'),
    url(r'^accounts/(\d+)/edit$', 'account_form', name='account-edit'),
    url(r'^members$', 'member_list', name='members'),
    url(r'^members/add$', 'member_form', name='member-add'),
    url(r'^members/(\w+)$', 'member', name='member'),
    url(r'^members/(\w+)/edit$', 'member_form', name='member-edit'),
    url(r'^rawlist/$', 'raw_list', name='membership-raw-list')
)
