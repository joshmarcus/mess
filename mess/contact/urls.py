from django.conf.urls.defaults import *
from mess.contact.models import Address, Email, Phone

urlpatterns = patterns('mess.contact.views',
    (r'^search_for$','search_for'),            
    #(r'^email/list/$', 'email_list'),
    #(r'^email/form/(\d{0,4})$', 'email_form'),
    #(r'^email/(\d{1,4})$', 'email'),
    #(r'^phone/list/$', 'phone_list'),
    #(r'^phone/form/(\d{0,4})$', 'phone_form'),
    #(r'^phone/(\d{1,4})$', 'phone'),
    #(r'^address/list/$', 'address_list'),
    url(r'^address/(\d+)/$', 'address', name='address'),
    url(r'^address/add/$', 'address_form', name='address_add'),
    url(r'^address/(\d+)/edit/$', 'address_form', name='address_edit'),
)
