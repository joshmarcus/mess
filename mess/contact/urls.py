from django.conf.urls.defaults import *
from contact.models import Address, Email, Phone

urlpatterns = patterns('mess.contact.views',
    (r'^email/list/$', 'email_list'),
    (r'^email/form/(\d{0,4})$', 'email_form'),
    (r'^email/(\d{1,4})$', 'email'),
    (r'^phone/list/$', 'phone_list'),
    (r'^phone/form/(\d{0,4})$', 'phone_form'),
    (r'^phone/(\d{1,4})$', 'phone'),
    (r'^address/list/$', 'address_list'),
    (r'^address/form/(\d{0,4})$', 'address_form'),
    (r'^address/(\d{1,4})$', 'address'),
)
