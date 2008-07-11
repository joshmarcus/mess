from django.conf.urls.defaults import *
from mess.membership.models import Member, Account

urlpatterns = patterns('mess.membership.views',
    url(r'^account/(\d{1,4})$', 'account', name='account'),
    url(r'^account/list/$', 'account_list', name='accounts'),
    url(r'^member/(\d{1,4})$', 'member', name='member'),
    url(r'^member/list/$', 'member_list', name='members'),
    #(r'^account/form/(\d{0,4})$', 'account_form'),    
    #(r'^member/form/(\d{0,4})$', 'member_form'),
)
