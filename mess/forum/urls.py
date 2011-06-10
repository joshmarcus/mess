from django.conf.urls.defaults import *

urlpatterns = patterns('mess.forum.views',
    url(r'^menu/$', 'menu', name='forum-menu'),
    url(r'^(\w+)/$', 'forum', name='forum'),
    url(r'^(\w+)/addpost/$', 'addpost', name='addpost'),
    url(r'^deletepost$', 'deletepost', name='deletepost'),
    url(r'^goto$','goto',name='goto'),
)
