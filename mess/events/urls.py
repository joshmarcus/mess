from django.conf.urls.defaults import *
from mess.events.models import *

urlpatterns = patterns('mess.events.views',
    url(r'^orientation/$', 'orientations', name="events-orientations"),
    url(r'^orientation/add$', 'orientation_form', name='events-orientation-add'),
    url(r'^orientation/(\d+)/edit$', 'orientation_form', name='events-orientation-edit'),
    url(r'^location/$', 'locations', name="events-locations"),
    url(r'^location/(\d+)/edit$', 'location_form', name="events-location-edit"),
    url(r'^location/add$', 'location_form', name='events-location-add'),
)
