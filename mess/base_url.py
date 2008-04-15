from django.conf.urls.defaults import *
from django.conf import settings 

base_url_path = r'^%s' % settings.PROJECT_URL[1:]

urlpatterns = patterns('',
    (base_url_path, include('mess.urls')),
)
