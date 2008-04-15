from django.conf.urls.defaults import *

urlpatterns = patterns('mess.people.views',
    (r'^$', 'people'),
    (r'^form/(\d{0,4})$', 'person_form'),
    (r'^(\d{1,4})/$', 'person'),
    (r'^search/$', 'search'),
)
