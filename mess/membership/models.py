from datetime import date

from django.db import models
from django.contrib.auth.models import User

from mess.people.models import Person
from mess.scheduling.models import Job

MEMBER_STATUS = (
    ('a', 'Active'),
    ('L', 'Leave of Absence'),
    ('q', 'Quit'),
    ('m', 'Missing'),  # Member has disappeared without notice.
    ('i', 'Inactive'),
)

WORK_STATUS = (
    ('e','Excused'),
    ('w', 'Working'),  # Member is active and has a job.
    ('n', 'Non-Working'),  # Such as a single parent.
)

CONTACT_PREF = (
    ('e', 'Email'),
    ('t', 'Telephone'),
)

class Member(models.Model):
    person = models.ForeignKey(Person, unique=True, related_name='member')
    status = models.CharField(max_length=1, choices=MEMBER_STATUS,
                            default='a', radio_admin=True)
    work_status = models.CharField(max_length=1, choices=WORK_STATUS,
                            default='w', radio_admin=True)
    account = models.ForeignKey('Account', related_name='primary_account',
                                verbose_name='Primary Account',
                                blank=True, null=True)
    date_joined = models.DateField(default=date(1990, 01, 01))
    has_key = models.BooleanField(default=False)
    job = models.ForeignKey(Job, blank=True, null=True,)
    contact_preference = models.CharField(max_length=1, 
            choices=CONTACT_PREF, default='e', radio_admin=True)

# I removed preferred phone and email -- if you think we need them we can
# put them back in.  Even CONTACT_PREF is questionable -- won't we, in
# reality, just default to email for everyone unless they don't have an
# email address, and use phone for times when we need immediate contact?
#    def _get_prefered_phone(self):
#        """ The Member's prefered phone. """
#        return getattr(self, 'phone_%s' % self.prefered_phone)
#
#    def _get_prefered_email(self):
#        """ The Member's prefered email address. """
#        return getattr(self, 'email_%s' % self.prefered_email)
#    
#    def _get_prefered_contact(self):
#        """ The Member's prefered contact. """
#        email = getattr(self, 'email_%s' % self.prefered_email)
#        phone = getattr(self, 'phone_%s' % self.prefered_phone)
#        contact = ''
#
#        if self.contact_by is 'e' and email:
#            contact = email
#        elif self.contact_by is 'p' and phone:
#            contact = phone
#        elif email:
#            contact = email
#        elif phone:
#            contact = phone 
#        else:
#            contact = 'None Defined'
#        return contact
#    contact = property(_get_prefered_contact)

    def __unicode__(self):
        return self.person.name

    class Meta:
        permissions = (
            ('can_edit_own', 'Can edit own'),
            ('can_view_list', 'Can view list'),
        )
        # can't order by ForeignKey
        #ordering = ['person']

    class Admin:
        pass


class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member, related_name='accounts',)
    can_shop = models.BooleanField()

    # Do we want to keep an account balance here?  It would mean some
    # replication of data because balance can be found by tracing 
    # transactions, but it might be nice to have here for easier lookups.
    # An account's balance would have to be updated with each related 
    # transaction.save().
    # Also, people really shouldn't have null balances.  Even if it's a 
    # new account, a deposit should have been made.
    # balance = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass
