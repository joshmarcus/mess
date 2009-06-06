from datetime import date
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# XXX: should these MEMBER_STATUSes go on Account instead?
MEMBER_STATUS = (
    ('a', 'Active'),
    ('L', 'Leave of Absence'),
    ('m', 'Missing'),  # Member has disappeared without notice.
    ('x', 'Missing Delinquent'),  # Member has disappeared, owing money/time
    ('d', 'Departed'),
#   ('i', 'Inactive'),
)
WORK_STATUS = (
    ('w', 'Workshift'),  # Member is active and should have a workshift
    ('c', 'Committee'), # Anything not tracked shift by shift
    ('e', 'Exempt'),     # Exemptions granted for kids, health, etc.
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

class MemberManager(models.Manager):
    'Custom manager to add extra methods'
    def active(self):
        return self.filter(status='a')

class Member(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    status = models.CharField(max_length=1, choices=MEMBER_STATUS,
                            default='a')
    work_status = models.CharField(max_length=1, choices=WORK_STATUS,
        default='w', help_text='This only matters for Active Members. \
        Workshift means they should have a workshift. \
        Committee means anything not tracked as a \
        regular shift, for example, COMMITTEE, BUSINESS/ORG, etc')
    has_key = models.BooleanField(default=False)
    #primary_account = models.ForeignKey('Account', blank=True, null=True)
    date_joined = models.DateField(default=date.today())
    date_missing = models.DateField(blank=True, null=True)
    date_departed = models.DateField(blank=True, null=True)

    objects = MemberManager()

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def name(self):
        return self.user.username

    @property
    def url(self):
        return reverse('member', args=[self.user.username])

    def next_shift(self):
        tasks = self.task_set.filter(time__gte=datetime.date.today()).order_by('time')
        if len(tasks):
            return tasks[0]
        else:
            return None

    def primary_account(self):
        try:
            primary = self.accounts.filter(
                    accountmember__primary_account=True)[0]
        except IndexError:
            try:
                primary = self.accounts.all()[0]
            except IndexError:
                primary = Account()
        return primary

    def autocomplete_label(self):
        if self.status == 'a':
            return '%s %s (%s)' % (self.user.first_name, self.user.last_name, 
                               self.primary_account().name)
        else:
            return '* %s %s (%s)' % (self.user.first_name, self.user.last_name,
                                self.primary_account().name)

    class Meta:
        ordering = ['user__username']


class LeaveOfAbsence(models.Model):
    """ Leave of absence periods for members. """
    member = models.ForeignKey(Member)
    start = models.DateField()
    end = models.DateField()

 
class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    #contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member, related_name='accounts', 
            through='AccountMember')
    can_shop = models.BooleanField(default=True)
    ebt_only = models.BooleanField()
    hours_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    deposit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # balance is updated with each transaction.save()
    balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    @property
    def active_member_count(self):
        return len(self.accountmember_set.filter(shopper=False).filter(member__status='a'))

    @property
    def url(self):
        return reverse('account', args=[self.id])

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class AccountMember(models.Model):
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    # account_contact displayed as "deposit holder" per shinara's request
    # -- gsf 2009-05-03
    account_contact = models.BooleanField(default=True, verbose_name="deposit holder")
    # primary_account isn't being displayed for now.  not needed according
    # to shinara -- gsf 2009-05-03
    primary_account = models.BooleanField(default=True)
    # is this member just a shopper on the account?
    shopper = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s: %s' % (self.account, self.member)

    class Meta:
        ordering = ['account', 'id']
    

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

