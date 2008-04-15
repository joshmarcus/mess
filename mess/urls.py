from django.conf.urls.defaults import *
from django.conf import settings 
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    (r'^$', 'mess.views.welcome'),
    (r'', include('mess.accounting.urls')),        
    (r'', include('mess.contact.urls')),            
    (r'', include('mess.membership.urls')),        
    (r'^people/', include('mess.people.urls')),      
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', logout),
)

# We're going to use the Django server in development, so we'll serve
# the static content for now.
if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root':'./media/'}),
    )

