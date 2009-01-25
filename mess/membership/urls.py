from django.conf.urls.defaults import *
from mess.membership import models
from autocomplete.views import autocomplete

autocomplete.register('account', models.Account.objects.all(), ('name',), limit=10, label='name')
autocomplete.register('member_with_paccount', models.Member.objects.all(), ('user__first_name__startswith','user__last_name__startswith','accounts__name__startswith'), limit=10, label=lambda m: m.name_and_paccount() )

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts$', 'accounts', name='accounts'),
    url(r'^accounts/add$', 'account_form', name='account-add'),
    url(r'^accounts/(\d+)$', 'account', name='account'),
    url(r'^accounts/(\d+)/edit$', 'account_form', name='account-edit'),
    url(r'^members$', 'members', name='members'),
    url(r'^members/add$', 'member_form', name='member-add'),
    url(r'^members/(\w+)$', 'member', name='member'),
    url(r'^members/(\w+)/edit$', 'member_form', name='member-edit'),
    url(r'^formset-form/(\w+)$', 'formset_form', name='membership-formset-form'),

    url(r'^(?P<username>\w+)/add_(?P<medium>\w+)/$', 'contact_form', name='membership-add-contact'),

    url(r'^(?P<username>\w+)/edit_(?P<medium>\w+)/(?P<id>\d+)$', 'contact_form', name='membership-edit-contact'),
    url(r'^(?P<username>\w+)/edit_address/(?P<id>\d+)$', 'contact_form', kwargs={'medium': 'address'}, name='membership-edit-address'),
    url(r'^(?P<username>\w+)/edit_email/(?P<id>\d+)$', 'contact_form', kwargs={'medium': 'email'}, name='membership-edit-email'),
    url(r'^(?P<username>\w+)/edit_phone/(?P<id>\d+)$', 'contact_form', kwargs={'medium': 'phone'}, name='membership-edit-phone'),

    url(r'^(?P<username>\w+)/remove_(?P<medium>\w+)/(?P<id>\d+)$', 'remove_contact', name='membership-remove-contact'),
    url(r'^(?P<username>\w+)/remove_address/(?P<id>\d+)$', 'remove_contact', kwargs={'medium': 'address'}, name='membership-remove-address'),
    url(r'^(?P<username>\w+)/remove_email/(?P<id>\d+)$', 'remove_contact', kwargs={'medium': 'email'}, name='membership-remove-email'),
    url(r'^(?P<username>\w+)/remove_phone/(?P<id>\d+)$', 'remove_contact', kwargs={'medium': 'phone'}, name='membership-remove-phone'),

    url('^autocomplete/(\w+)/$', autocomplete, name='membership-autocomplete'),
    #url(r'^rawlist/$', 'raw_list', name='membership-raw-list')
)
