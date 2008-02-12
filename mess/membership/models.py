from datetime import date

from django.db import models
from django.contrib.auth.models import User

from mess.people.models import Person
from mess.work.models import Job

MEMBER_STATUS = (
    ('a', 'Active'),
    ('w', 'Working'),  # Member is active and has a job.
    ('n', 'Non-Working'),  # Such as a single parent.
    ('L', 'Leave of Absence'),
    ('q', 'Quit'),
    ('m', 'Missing'),  # Member has disappeared without notice.
    ('i', 'Inactive'),
)

CONTACT_PREF = (
    ('e', 'Email'),
    ('t', 'Telephone'),
)

class Member(models.Model):
    person = models.ForeignKey(Person)
    # It seems that some of the choices in MEMBER_STATUS could overlap,
    # in which case they should be split into separate fields, such as
    # "status" and "active".  I may just be reading them wrong, though.
    status = models.CharField(max_length=1, choices=MEMBER_STATUS,
                            default='a', radio_admin=True)
    date_joined = models.DateField(default=date(1990, 01, 01))
    has_key = models.BooleanField()
    job = models.ForeignKey(Job)
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
        pass

    class Admin:
        pass
#        list_display = ('__str__', 'account',)
#        fields = (
#            (None, {
#                'fields': (('given', 'middle', 'family'),
#                            ('user', 'password'), 'date_joined', 'status',
#                            'role', ('has_key', 'job', 'address')),
#                }),
#            ('Accounts', {
#                'classes': 'collapse',
#                'fields' : (('account', 'accounts'),),
#                }),
#            ('Contact', {
#                'classes': 'collapse',
#                'fields' : (('contact_by', 'prefered_email', 'prefered_phone'),
#                            ('email_1', 'email_1_loc', 'email_1_pub'),
#                            ('email_2', 'email_2_loc', 'email_2_pub'),
#                            ('email_3', 'email_3_loc', 'email_3_pub'),
#                            ('phone_1', 'phone_1_ext', 'phone_1_type',
#                                'phone_1_loc','phone_1_pub'),
#                            ('phone_2', 'phone_2_ext', 'phone_2_type',
#                                'phone_2_loc', 'phone_2_pub'),
#                            ('phone_3', 'phone_3_ext', 'phone_3_type',
#                                'phone_3_loc',  'phone_3_pub'),
#                            ),
#                }),
#        )

class Account(models.Model):
# Regarding balance(), just reference the variable instead of creating a
# method to get it.  a.balance and a.balance() should be the same.  That
# is,
# >>> a = Account.objects.get(id=1)
# >>> a.balance  
# 72.06
# >>> a.balance()
# 72.06
#    def balance():
#        return balance

    name = models.CharField(max_length=50, unique=True)
    contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member)
    can_shop = models.BooleanField()

    # Do we want to keep an account balance here?  It would mean some
    # replication of data because balance can be found by tracing 
    # transactions, but it might be nice to have here for easier lookups.
    # An account's balance would have to be updated with each related 
    # transaction.save().
    # Also, people really shouldn't have null balances.  Even if it's a 
    # new account, a deposit should have been made.
    balance = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass
