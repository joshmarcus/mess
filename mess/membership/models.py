from datetime import date
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
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
        return self.filter(date_missing__isnull=True, 
                date_departed__isnull=True)

    def inactive(self):
        return self.filter(Q(date_missing__isnull=False)|
                Q(date_departed__isnull=False))


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
    def current_loa(self):
        loa_set = self.leaveofabsence_set.filter(
                start__lte=datetime.datetime.now(),
                end__gte=datetime.datetime.now())
        if loa_set:
            return loa_set[0]
        
    @property
    def is_active(self):
        return not (self.date_missing or self.date_departed)

    @property
    def is_on_loa(self):
        return bool(self.current_loa)

    @property
    def is_cashier_today(self):
        shifts = self.task_set.filter(job__name='Cashier', time__range=(
            datetime.date.today(), datetime.date.today()+datetime.timedelta(1)))
        return bool(shifts.count())

    @property
    def name(self):
        return self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('member', [self.user.username])

    def next_shift(self):
        tasks = self.task_set.filter(time__gte=datetime.date.today()).order_by('time')
        if tasks.count():
            return tasks[0]
        else:
            return None

    def remove_from_shifts(self, start, end=None):
        '''
        Removes member from workshifts that haven't happened yet.
        End date is optional.
        '''

        # handle start and end dates in the past
        if start < datetime.date.today():
            start = datetime.date.today()
        if end and end < datetime.date.today():
            return          # end date in past; don't mess with shifts.

        # switch all post-start tasks to new recur rule; 
        # set old recur_rule.until as our start date.
        tasks = self.task_set.filter(time__gte=start)
        r_rule_switch = {}
        for task in tasks:
            if task.recur_rule:
                if task.recur_rule in r_rule_switch:
                    new_rule = r_rule_switch[task.recur_rule]
                else:
                    new_rule = task.duplicate_recur_rule()
                    task.recur_rule.until = start
                    task.recur_rule.save()
                    r_rule_switch[task.recur_rule] = new_rule
                task.recur_rule = new_rule

            # task is inside LOA and should be released for one-time fill.
            # i.e. no longer point to any recur rule
            if end:
                if task.time.date() <= end:
                    task.recur_rule = None
                    task.member = task.account = None
                    
            # permanently remove from workshift (no end date)
            else:
                task.member = task.account = None

            task.save()


    def get_primary_account(self):
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
        if self.is_active:
            return '%s %s (%s)' % (self.user.first_name, self.user.last_name, 
                               self.get_primary_account().name)
        else:
            return '* %s %s (%s)' % (self.user.first_name, self.user.last_name,
                                self.get_primary_account().name)

    @property
    def verbose_status(self):
        if self.date_departed:
            return 'Departed since %s' % self.date_departed
        elif self.date_missing:
            return 'Missing since %s' % self.date_missing
        else:
            if self.is_on_loa:
                return 'Active, but on leave until %s' % self.current_loa.end
            return 'Active'

    class Meta:
        ordering = ['user__username']

def cashier_permission(request):
    ''' 
    used as a template context processor before showing 'cashier' tab 
    bool(returnvalue['can_cashier_now']) is trusted by template
    bool(returnvalue) is trusted by accounting/views
    '''
    if not request.user.is_authenticated():
        return {}     # no permission, bool({}) = False
    if request.user.is_staff:
        return {'can_cashier_now':True}
    if (request.user.get_profile().is_cashier_today
        and request.META['REMOTE_ADDR'] == settings.MARIPOSA_IP):
        return {'can_cashier_now':True}
    return {}     # no permission, bool({}) = False

class LeaveOfAbsence(models.Model):
    """ Leave of absence periods for members. """
    member = models.ForeignKey(Member)
    start = models.DateField()
    end = models.DateField()

 
class AccountManager(models.Manager):
    'Custom manager to add extra methods'
    def active(self):
        return self.filter(members__date_missing__isnull=True, 
                members__date_departed__isnull=True).distinct()

    def inactive(self):
        return self.exclude(members__date_missing__isnull=True, 
                members__date_departed__isnull=True)


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

    objects = AccountManager()

    @property
    def active_member_count(self):
        return len(self.accountmember_set.filter(shopper=False).filter(
            member__date_missing__isnull=True, 
            member__date_departed__isnull=True))

    def autocomplete_label(self):
        if self.active_member_count:
            return self.name
        else:
            return '* '+self.name

    @models.permalink
    def get_absolute_url(self):
        return ('account', [self.id])

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

