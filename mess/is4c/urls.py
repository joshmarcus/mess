from django.conf.urls.defaults import *

urlpatterns = patterns('mess.is4c.views',
    url(r'^$', 'index', name='is4c-index'),
    url(r'^account/(\d+)/$', 'account', name='is4c-account'),
)
