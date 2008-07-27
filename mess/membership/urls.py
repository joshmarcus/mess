from django.conf.urls.defaults import *

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts/$', 'account_list', name='accounts'),
    url(r'^accounts/(\d{1,4})$', 'account', name='account'),
    url(r'^members/$', 'member_list', name='members'),
    url(r'^members/(\w+)$', 'member', name='member'),
    url(r'^members/(\w+)/edit$', 'member_form', name='member-edit'),
    #(r'^account/form/(\d{0,4})$', 'account_form'),    
)
