from django.conf.urls.defaults import *

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts$', 'account_list', name='accounts'),
    url(r'^accounts/add$', 'account_form', name='account-add'),
    url(r'^accounts/(\d+)$', 'account', name='account'),
    url(r'^accounts/(\d+)/edit$', 'account_form', name='account-edit'),
    url(r'^members$', 'member_list', name='members'),
    url(r'^members/add$', 'member_add', name='member-add'),
    url(r'^members/(\w+)$', 'member', name='member'),
    url(r'^members/(\w+)/edit$', 'member_edit', name='member-edit'),
    url(r'^contactform/(\w+)$', 'contact_form_for_formset', name='membership-contact-form'),
    url(r'^(\w+)/add_(\w+)/$', 'add_contact', name='membership-add-contact'),
    url(r'^(\w+)/remove_(\w+)/(\d+)$', 'remove_contact', name='membership-remove-contact'),
    #url(r'^rawlist/$', 'raw_list', name='membership-raw-list')
)
