from django.conf import settings 
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('mess.core.urls')),
    (r'^accounting/', include('mess.accounting.urls')),        
    (r'^membership/', include('mess.membership.urls')),        
    (r'^forum/', include('mess.forum.urls')),
    (r'^fundraising/', include('mess.telethon.urls')),
    (r'^reporting/', include('mess.reporting.urls')),        
    (r'^scheduling/', include('mess.scheduling.urls')),        

    #url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^passwordchange/$', auth_views.password_change, name='auth_password_change'),
    url(r'^passwordchange/done/$', auth_views.password_change_done, name='auth_password_change_done'),
    url(r'^passwordreset/$', auth_views.password_reset, name='auth_password_reset'),
    url(r'^passwordreset/done/$', auth_views.password_reset_done, name='auth_password_reset_done'),
    url(r'^passwordreset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, name='auth_password_reset_confirm'),
    url(r'^passwordreset/complete/$', auth_views.password_reset_complete, name='auth_password_reset_complete'),

    ('^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('django.views.generic.simple', 
    (r'^styleguide$', 'direct_to_template', {'template': 'styleguide.html'}),
)

# We're going to use the Django server in development, so we'll serve
# the static content for now.
if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )

