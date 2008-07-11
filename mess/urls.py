from django.conf import settings 
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, logout_then_login

urlpatterns = patterns('',
    (r'^accounting/', include('mess.accounting.urls')),        
    (r'^contact/', include('mess.contact.urls')),            
    (r'^membership/', include('mess.membership.urls')),        
    (r'^people/', include('mess.people.urls')),
    (r'^reporting/', include('mess.reporting.urls')),        
    
    url(r'^$', login, {'template_name': 'welcome.html'}, 'login'),
    url(r'^logout/$', logout_then_login, name='logout'),

    (r'^admin/', include('django.contrib.admin.urls')),
)

# We're going to use the Django server in development, so we'll serve
# the static content for now.
if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root':'./media/'}),
    )

