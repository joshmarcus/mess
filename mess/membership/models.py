from datetime import date
import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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
EXEMPTION_TYPES = (
    ('k', 'Kids'),
    ('s', 'Seniors'),
    ('c', 'Caretaker'),
    ('p', 'Single Parent'),
    ('h', 'Health'),
    ('S', 'Special'),
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
today = datetime.date.today()

class MemberManager(models.Manager):
    'Custom manager to add extra methods'
    def active(self):
        return self.filter(date_missing__isnull=True, 
                date_departed__isnull=True)

    def inactive(self):
        return self.filter(Q(date_missing__isnull=False)|
                Q(date_departed__isnull=False))

    def active_not_LOA(self):
        return self.active().exclude(leaveofabsence__start__lte=today,
                                     leaveofabsence__end__gt=today)

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
    card_number = models.CharField(max_length=128, blank=True, null=True)
    card_facility_code = models.CharField(max_length=128, blank=True, 
            null=True)
    card_type = models.CharField(max_length=128, blank=True, null=True)

    objects = MemberManager()

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def current_loa(self):
        loa_set = self.leaveofabsence_set.filter(start__lte=today,end__gt=today)
        if loa_set.count():
            return loa_set[0]
        
    @property
    def is_active(self):
        return not (self.date_missing or self.date_departed)

    @property
    def is_on_loa(self):
        return bool(self.current_loa)

    @property
    def is_cashier_today(self):
        shifts_today = self.task_set.filter(time__range=(
            datetime.date.today(), datetime.date.today()+datetime.timedelta(1)))
        cashier_shifts_today = shifts_today.filter(job__name__in=[
            'Cashier','After Hours Billing'])
        return bool(cashier_shifts_today.count())

    @property
    def name(self):
        return self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('member', [self.user.username])

    def next_shift(self):
        tasks = self.task_set.filter(time__gte=datetime.date.today())
        if tasks.count():
            return tasks[0]

    def regular_shift(self):
        tasks = self.task_set.filter(time__gte=datetime.date.today(),
                recur_rule__isnull=False)
        if tasks.count():
            return tasks[0]

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

    def date_orientation(self):
        orientations = self.task_set.filter(job__name='Orientation Attendee')
        if orientations.count():
            return orientations[0].time.date()

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
    end = models.DateField(help_text="Remember!: Editing a Leave of absense directly does not affect member's workshifts.  Please remove them manually from any workshifts that fall within the leave.")
    


class WorkExemption(models.Model):
    """ Work exemptions for members. """
    type = models.CharField(max_length=1, choices=EXEMPTION_TYPES, default='k')
    member = models.ForeignKey(Member)
    start = models.DateField()
    end = models.DateField()


class AccountManager(models.Manager):
    'Custom manager to add extra methods'
    def active(self):
        return self.filter(members__isnull=False,
                members__date_missing__isnull=True, 
                members__date_departed__isnull=True).distinct()

    def inactive(self):
        return self.exclude(members__isnull=False,
                members__date_missing__isnull=True, 
                members__date_departed__isnull=True)

    def active_not_LOA(self):  # will show up on cash sheets
        am_active_not_LOA = AccountMember.objects.filter(
                shopper=False, account_contact=True,
                member__in=Member.objects.active_not_LOA())
        return self.filter(accountmember__in=am_active_not_LOA).distinct()


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
        return self.accountmember_set.filter(shopper=False).filter(
            member__date_missing__isnull=True, 
            member__date_departed__isnull=True).count()

    def billable_member_count(self):
        ''' active members MINUS anyone on leave of absence '''
        return self.accountmember_set.filter(shopper=False).filter(
            member__date_missing__isnull=True,
            member__date_departed__isnull=True).exclude(
            member__leaveofabsence__start__lte=today,
            member__leaveofabsence__end__gt=today).count()
    active_no_loa = property(billable_member_count)

    def deposit_holders(self):
        return self.accountmember_set.filter(
            member__date_missing__isnull=True,
            member__date_departed__isnull=True,
            account_contact=True)   # account_contact flag used for depositors

    def non_deposit_holders(self):
        return self.accountmember_set.filter(
            member__date_missing__isnull=True,
            member__date_departed__isnull=True,
            account_contact=False)   # account_contact flag used for depositors

    def departed_members(self):
        return self.accountmember_set.filter(
            Q(member__date_missing__isnull=False) |
            Q(member__date_departed__isnull=False))

    def autocomplete_label(self):
        if self.active_member_count:
            return self.name
        else:
            return '* '+self.name

    @models.permalink
    def get_absolute_url(self):
        return ('account', [self.id])

    def get_hours_balance_history_url(self):
        return reverse('hours_balance_changes')+'?account='+str(self.id)

    def members_leaveofabsence_set(self):
        return LeaveOfAbsence.objects.filter(member__accounts=self)

    def workhist(self):
        '''
        Generates the work history object used to produce the workhistory calendar on account page.
        complex data structures here:
        workhist[] is an array of weeks
        each week is a {} dictionary of {'days':[array], 'tasks':[array], 
           'newmonth' and 'newyear'} (newmonth and newyear flags show month 
           alongside the calendar)
        each day is a {} dictionary of {'week':(parent-pointer), 'date':(number),
           'workflag':(flag for highlighting), 'task':last-task}
        '''
        workhist = []
        dayindex = {}
        today = datetime.date.today()
        lastsunday = today - datetime.timedelta(days=today.weekday()+1)
        try:
            oldesttime = self.task_set.all().order_by('time')[0].time
            oldestweeks = ((today - oldesttime.date()).days / 7) + 2
            oldestweeks = max(oldestweeks, 16)
        except IndexError:
            oldestweeks = 16
        for weeksaway in range(-oldestweeks,52):
            week = {'tasks':[]}
            if weeksaway == -12:
                week['flagcurrent'] = True
            elif weeksaway == 7:
                week['flagfuture'] = True
            firstday = lastsunday + datetime.timedelta(days=7*weeksaway)
            week['days'] = [{'week':week} for i in range(7)]
            for i in range(7):
                week['days'][i]['date'] = firstday + datetime.timedelta(days=i)
                dayindex[week['days'][i]['date']] = week['days'][i]
            if 7 <= week['days'][6]['date'].day < 14:
                week['newmonth'] = week['days'][6]['date']
            elif 14 <= week['days'][6]['date'].day < 21:
                week['newyear'] = week['days'][6]['date'].year
            workhist.append(week)
        for task in self.task_set.all():
            if task.time.date() in dayindex:
                day = dayindex[task.time.date()]
                if 'workflag' in day:
                    day['workflag'] = 'complex-workflag'
                else:
                    day['workflag'] = task.simple_workflag
                day['task'] = task
                day['week']['tasks'].append(task)
        for leave in self.members_leaveofabsence_set():
            for dayofleave in daterange(leave.start, leave.end):
                if dayofleave not in dayindex: 
                    continue
                day = dayindex[dayofleave]
                if 'workflag' not in day:
                    day['workflag'] = 'LOA'
        dayindex[today]['istoday'] = True
        return workhist        

    def next_shift(self):
        tasks = self.task_set.filter(time__gte=datetime.date.today())
        if tasks.count():
            return tasks[0]

    def verbose_balance(self):
        if self.balance > 0:
            return 'Owes %.2f' % self.balance
        elif self.balance < 0:
            return 'Has credit of (%.2f)' % -self.balance
        else:
            return 'Zero balance'

    def owes_or_credit(self):
        if self.balance > 0:
            return 'Money Owed'
        else:
            return 'Credit'

    def hours_owed_or_banked(self):
        if self.hours_balance > 0:
            return 'Owed'
        else:
            return 'Banked'

    def balance_on(self, time):
        newest_trans = self.transaction_set.filter(
                       timestamp__lt=time).order_by('-timestamp')
        if newest_trans.count():
            return newest_trans[0].account_balance

    def max_allowed_to_owe(self):
        active_members = self.active_member_count
        if active_members == 0:
            return 0
        sixmonthsago = datetime.date.today() - datetime.timedelta(6*30)
        oldmembers = self.accountmember_set.filter(shopper=False,
                        member__date_joined__lt=sixmonthsago).count()
        if oldmembers:
            return active_members * Decimal('25.00')
        else:
            return active_members * Decimal('5.00')

    def must_pay(self):
        max_allowed_to_owe = self.max_allowed_to_owe()
        if self.balance > max_allowed_to_owe:
            return self.balance - max_allowed_to_owe

    def must_work(self):
        if self.hours_balance > Decimal('0.03'):
            return self.hours_balance

    def obligations(self):
        obligations = self.billable_member_count()
        if not obligations:
            if self.active_member_count:
                return 'On Leave'
            return
        for am in self.accountmember_set.all():
            if (am.member.regular_shift()
                    or (am.member.work_status in 'ec' and not am.shopper)):
                obligations -= 1
        if obligations:
            return 'Needs Shift'

    def frozen_flags(self):
        flags = []
        active_members = self.active_member_count
        # must pay?
        if self.balance > 0:
            sixmonthsago = datetime.date.today() - datetime.timedelta(6*30)
            oldmembers = self.members.filter(date_joined__lt=sixmonthsago)
            if oldmembers.count():
                max_balance = active_members * Decimal('25.00')
            else:
                max_balance = active_members * Decimal('5.00')
            if self.balance > max_balance:
                flags.append('MUST PAY') # %s' % (self.balance - max_balance))
        # must work?
        if self.hours_balance > Decimal('0.03'):
            flags.append('MUST WORK')
        if not self.can_shop:
            flags.append('CANNOT SHOP')
        if not active_members:
            flags.append('ACCOUNT CLOSED')
        return flags

    def notice_flags(self):
        flags = []
        obligations = self.billable_member_count()
        if not obligations and self.active_member_count:
            flags.append('On Leave')
        satisfactions = self.accountmember_set.filter(
            Q(member__work_status__in='ec', shopper=False) |
            Q(member__task__time__gte=datetime.date.today(), 
              member__task__recur_rule__isnull=False)).count()
        if obligations > satisfactions:
            flags.append('Needs Shift')
        if self.ebt_only:
            flags.append('EBT Only')
        return flags

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

    def save(self, *args, **kwargs):
        ''' stick new email address onto the user also '''
        user = self.member.user
        user.email = self.email
        user.save()
        super(Email, self).save(*args, **kwargs)


class Phone(models.Model):
    member = models.ForeignKey(Member, related_name='phones')
    type = models.CharField(max_length=1, choices=PHONE_TYPES, default='h')
    number = models.CharField(max_length=20)

    def __unicode__(self):
        return self.number

def daterange(start, end):
    while start < end:
        yield start
        start += datetime.timedelta(1)

