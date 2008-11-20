from datetime import date

from django.db import models
from django.contrib.auth.models import User

# XXX: should these MEMBER_STATUSes go on Account instead?
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
 
class Member(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    status = models.CharField(max_length=1, choices=MEMBER_STATUS,
                            default='a')
    work_status = models.CharField(max_length=1, choices=WORK_STATUS,
                            default='w')
    has_key = models.BooleanField(default=False)
    #primary_account = models.ForeignKey('Account', blank=True, null=True)
    date_joined = models.DateField(default=date.today())

    def __unicode__(self):
        return self.user.get_full_name()

    def primary_account(self):
        try:
            primary = self.accounts.get(accountmember__primary_account=True)
        except Account.DoesNotExist:
            primary = self.accounts.all()[0]
        return primary

    class Meta:
        ordering = ['user__username']


class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    #contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member, related_name='accounts', 
            through='AccountMember')
    can_shop = models.BooleanField(default=True)
    # balance is updated with each transaction.save()
    balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class AccountMember(models.Model):
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    # is this member the contact for the account?
    account_contact = models.BooleanField(default=True)
    # is this the primary account for the member?
    primary_account = models.BooleanField(default=True)
    # is this member just a shopper on the account?
    shopper = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s: %s' % (self.account, self.member)

    class Meta:
        ordering = ['account']
    

# possibly include IM and URL classes at some point

class Address(models.Model):
    member = models.ForeignKey(Member, related_name='addresses')
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


class Email(models.Model):
    member = models.ForeignKey(Member, related_name='emails')
    type = models.CharField(max_length=1, choices=EMAIL_TYPES, default='p')
    email = models.EmailField()

    def __unicode__(self):
        return self.email


class Phone(models.Model):
    member = models.ForeignKey(Member, related_name='phones')
    type = models.CharField(max_length=1, choices=PHONE_TYPES, default='h')
    number = models.CharField(max_length=20)

    def __unicode__(self):
        return self.number

