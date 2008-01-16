from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    (r'^about/$', 'mess.misc.views.about'),
    (r'^contact/$', 'mess.misc.views.contact'),
    (r'^feedback/$', 'mess.misc.views.feedback'),
    (r'^members_list/$', 'mess.membership.views.members_list'),
    (r'^member/(\d{1,4}|\w{3,20})/$', 'mess.membership.views.member'),
    (r'^accounts_list/$', 'mess.membership.views.accounts_list'),
    (r'^account/(\d{1,4})/$', 'mess.membership.views.account'),
    (r'^job_list/$', 'mess.work.views.jobs'),
    (r'^job/(\d{1,3}|\w{3,20})/$', 'mess.work.views.job'),

    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout),
)
