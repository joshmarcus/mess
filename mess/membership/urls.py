from django.conf.urls.defaults import *

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts$', 'accounts', name='accounts'),
    url(r'^accounts/add$', 'account_add', name='account-add'),
    url(r'^accounts/(\d+)$', 'account', name='account'),
    url(r'^accounts/(\d+)/edit$', 'account_edit', name='account-edit'),
    url(r'^members$', 'members', name='members'),
    url(r'^members/add$', 'member_add', name='member-add'),
    url(r'^members/(\w+)$', 'member', name='member'),
    url(r'^members/(\w+)/edit$', 'member_edit', name='member-edit'),
    url(r'^contactformset/(\w+)$', 'contact_formset_form', name='membership-contact-formset'),
    url(r'^(\w+)/add_(\w+)/$', 'add_contact', name='membership-add-contact'),
    url(r'^(\w+)/edit_address/(\d+)$', 'edit_address', name='membership-edit-address'),
    url(r'^(\w+)/edit_email/(\d+)$', 'edit_email', name='membership-edit-email'),
    url(r'^(\w+)/edit_phone/(\d+)$', 'edit_phone', name='membership-edit-phone'),
    url(r'^(\w+)/remove_address/(\d+)$', 'remove_address', name='membership-remove-address'),
    url(r'^(\w+)/remove_phone/(\d+)$', 'remove_phone', name='membership-remove-phone'),
    url(r'^(\w+)/remove_email/(\d+)$', 'remove_email', name='membership-remove-email'),
    #url(r'^(\w+)/remove_(\w+)/(\d+)$', 'remove_contact', name='membership-remove-contact'),
    #url(r'^rawlist/$', 'raw_list', name='membership-raw-list')
)
