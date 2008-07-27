from django.conf.urls.defaults import *

urlpatterns = patterns('mess.membership.views',
    url(r'^account/(\d{1,4})$', 'account', name='account'),
    url(r'^account/list/$', 'account_list', name='accounts'),
    url(r'^members/$', 'member_list', name='members'),
    url(r'^members/(\w+)$', 'member', name='member'),
    #(r'^account/form/(\d{0,4})$', 'account_form'),    
    #(r'^member/form/(\d{0,4})$', 'member_form'),
)
