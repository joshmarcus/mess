from datetime import date

from django.db import models
from django.contrib.auth.models import User

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
ADDRESS_TYPES = (
    ('h','Home'),
    ('w','Work'),
    ('o','Other'),
)
PHONE_TYPES = (
    ('h','Home'),
    ('w','Work'),
    ('m','Mobile'),
    ('o','Other'),
)
EMAIL_TYPES = (
    ('p','Personal'),
    ('w','Work'),
    ('s','School'),
    ('o','Other'),
)
 
# possibly include IM and URL classes at some point

class Address(models.Model):
    type = models.CharField(max_length=1, choices=ADDRESS_TYPES, default='h')
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, default='Philadelphia')
    # state is CharField to allow for international
    state = models.CharField(max_length=50, default='PA')
    # postal_code is CharField for the same reason as state
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='USA')
    
    def __unicode__(self):
        if self.address2:
            return ('%s, %s' % (self.address1, self.address2))
        else:
            return self.address1

    class Meta:
        verbose_name_plural = 'Addresses'


class Phone(models.Model):
    type = models.CharField(max_length=1, choices=PHONE_TYPES, default='h')
    number = models.CharField(max_length=20)

    def __unicode__(self):
        return self.number


class Email(models.Model):
    type = models.CharField(max_length=1, choices=EMAIL_TYPES, default='p')
    email = models.EmailField()

    def __unicode__(self):
        return self.email


class Member(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    status = models.CharField(max_length=1, choices=MEMBER_STATUS,
                            default='a')
    work_status = models.CharField(max_length=1, choices=WORK_STATUS,
                            default='w')
    has_key = models.BooleanField(default=False)
    primary_account = models.ForeignKey('Account', blank=True, null=True)
    date_joined = models.DateField(default=date(1990, 01, 01))
    addresses = models.ManyToManyField(Address, blank=True, null=True)
    phones = models.ManyToManyField(Phone, blank=True, null=True)
    emails = models.ManyToManyField(Email, blank=True, null=True)

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['user__username']


class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member, related_name='accounts',)
    can_shop = models.BooleanField(default=True)
    # balance is updated with each transaction.save()
    balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
