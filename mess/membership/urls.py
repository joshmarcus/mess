from django.conf.urls.defaults import *
from membership.models import Member

urlpatterns = patterns('mess.membership.views',
    (r'^member/list/$', 'member_list'),
    (r'^member/form/(\d{0,4})$', 'member_form'),
    (r'^member/(\d{1,4})$', 'member'),
    (r'^account/list/$', 'account_list'),
    (r'^account/(\d{1,4})$', 'account'),
)
