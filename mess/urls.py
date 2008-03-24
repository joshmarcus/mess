from django.conf.urls.defaults import *
from django.conf import settings 
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    (r'^mess/$', 'mess.views.welcome'),
    (r'^mess/', include('mess.accounting.urls')),        
    (r'^mess/', include('mess.contact.urls')),            
    (r'^mess/', include('mess.membership.urls')),        
    (r'^mess/', include('mess.people.urls')),      
    (r'^mess/accounts/login/$',  login),
    (r'^mess/accounts/logout/$', logout),
    (r'^mess/admin/', include('django.contrib.admin.urls')),
)

# We're going to use the Django server in development, so we'll serve
# also the static content.
if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^mess/media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root':'./media/'}),
    )

