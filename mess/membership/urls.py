from django.conf.urls.defaults import *
from mess.membership import models
from mess.autocomplete.views import autocomplete
from django.db.models import Q
from django.contrib.auth import views as auth_views

autocomplete.register('account', models.Account.objects.all(), ('name__istartswith',), limit=10, label='name')

# create hook to branch autocomplete filter: '* = include inactive'
# (this doesn't belong here in urls.py, but where should it live?)
def member_spiffy_filter(query):
    if '*' in query:
        plain_query = query.strip('* ')
        return (Q(user__first_name__istartswith=plain_query) |
                Q(user__last_name__istartswith=plain_query) |
                Q(accounts__name__istartswith=plain_query))
    else:
        return (Q(date_departed__isnull=True) & 
                Q(date_missing__isnull=True) &
                   (Q(user__first_name__istartswith=query) |
                    Q(user__last_name__istartswith=query) |
                    Q(accounts__name__istartswith=query)))

autocomplete.register('member_spiffy', models.Member.objects.all(), member_spiffy_filter, limit=10, label=lambda m: m.autocomplete_label() )

def account_spiffy_filter(query):
    if '*' in query:
        plain_query = query.strip('* ')
        return Q(name__istartswith=plain_query)
    else:
        return (Q(members__date_missing__isnull=True) &
                Q(members__date_departed__isnull=True) &
                Q(name__istartswith=query))

autocomplete.register('account_spiffy', models.Account.objects.all(), account_spiffy_filter, limit=10, label=lambda a: a.autocomplete_label() )

urlpatterns = patterns('mess.membership.views',
    url(r'^accounts$', 'accounts', name='accounts'),
    url(r'^accounts/add$', 'account_form', name='account-add'),
    url(r'^accounts/(\d+)$', 'account', name='account'),
    url(r'^accounts/(\d+)/edit$', 'account_form', name='account-edit'),
    url(r'^accounts/(\d+)/depart$', 'depart_account', name='depart-account'),
    url(r'^accounts/(\d+)/loa$', 'loa_account', name='loa-account'),
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

    url(r'^autocomplete/(\w+)/$', autocomplete, name='membership-autocomplete'),
    url(r'^accountmemberflags/$', 'accountmemberflags', name='accountmemberflags'),

    url(r'^(?P<username>\w+)/adminresetpassword/$', 'admin_reset_password', name='admin_reset_password'),

    #url(r'^rawlist/$', 'raw_list', name='membership-raw-list')
    #url('^junkx/(\w+)/$', junk, name='junkx'),
)
