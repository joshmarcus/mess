from django.conf import settings 
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout, logout_then_login

admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounting/', include('mess.accounting.urls')),        
    (r'^membership/', include('mess.membership.urls')),        
    #(r'^profiles/', include('mess.profiles.urls')),
    (r'^reporting/', include('mess.reporting.urls')),        
    (r'^scheduling/', include('mess.scheduling.urls')),        
    
    url(r'^$', login, {'template_name': 'welcome.html'}, 'login'),
    url(r'^logout$', logout_then_login, name='logout'),

    ('^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('django.views.generic.simple', 
    (r'^styleguide$', 'direct_to_template', {'template': 'styleguide.html'}),
    (r'^login$', 'direct_to_template', {'template': 'login.html'}),
)

# We're going to use the Django server in development, so we'll serve
# the static content for now.
if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )

