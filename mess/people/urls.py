from django.conf.urls.defaults import *

urlpatterns = patterns('mess.people.views',
    (r'^people/$', 'people'),
    (r'^person/form/(\d{0,4})$', 'person_form'),
    (r'^person/(\d{1,4})$', 'person'),
    (r'^people/search$', 'search'),
)
