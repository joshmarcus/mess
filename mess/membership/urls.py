from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from membership.models import Member

member_info = {
    'queryset': Member.objects.all(),
}


urlpatterns = patterns('mess.membership.views',
    (r'^member/list/$', 'member_list'),
    (r'^member/form/(\d{0,4})$', 'member_form'),
    (r'^member/(\d{1,4})$', 'member'),
    (r'^account/list/$', 'account_list'),
    (r'^account/(\d{1,4})$', 'account'),
)

urlpatterns = patterns('',
    (r'^gen_mem_list$', 'object_list', member_info),

)
