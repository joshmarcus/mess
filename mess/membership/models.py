from datetime import date
import datetime
import string
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Min

# import scheduling models to figure what tasks a member has
from mess.scheduling import models as s_models

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
    ('n', 'No-Workshift'), # Non-working member
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

    def present(self):
        return self.active().exclude(leaveofabsence__in=
                                     LeaveOfAbsence.objects.current())

class Member(models.Model):
    user = models.ForeignKey(User, unique=True)
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
    equity_held = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    equity_due = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    equity_increment = models.DecimalField(max_digits=8, decimal_places=2, default=25)

    objects = MemberManager()

    def __unicode__(self):
        return self.user.get_full_name()

    def equity_target(self):
        shared_house_size = 0
        for acct in self.accounts.filter(shared_address=True):
            shared_house_size = max(shared_house_size, acct.active_member_count)
        if shared_house_size >= 5:
            return Decimal("125.00")
        if shared_house_size >= 3:
            return Decimal("150.00")
        return Decimal("200.00")

    def skills(self):
        return s_models.Skill.objects.filter(
            trained_by__task__in=self.task_set.worked()).distinct()

    def untrained(self):
        return s_models.Skill.objects.exclude(
            trained_by__task__in=self.task_set.worked()).distinct()

    def qualified_tasks(self, possible=None):
        if possible is None:
            possible = s_models.Task.objects.unassigned_future()
        return possible.exclude(job__skills_required__in=self.untrained())
        
    @property
    def current_loa(self):
        loa_set = self.leaveofabsence_set.current()
        if loa_set.count():
            return loa_set[0]
        
    @property
    def is_active(self):
        return not (self.date_missing or self.date_departed)

    @property
    def is_on_loa(self):
        return bool(self.current_loa)

    @property
    def is_cashier_recently(self):
        shifts_recently = self.task_set.filter(time__range=(
            datetime.date.today()-datetime.timedelta(180), datetime.date.today()))
        cashier_shifts_recently = shifts_recently.filter(job__name__in=[
            'Cashier','After Hours Billing'], hours_worked__gt=0)
        return bool(cashier_shifts_recently.count())

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
                    accountmember__shopper=False)[0]
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

    def date_joined_is_realistic(self):
        if self.date_joined > datetime.date(1970,1,1):
            return self.date_joined

    def date_orientation(self):
        orientations = self.task_set.filter(job__name='Orientation Attendee')
        if orientations.count():
            return orientations[0].time.date()

    class Meta:
        ordering = ['user__username']

class LeaveOfAbsenceManager(models.Manager):
    def current(self):
        return self.filter(start__lte=today, end__gt=today)

class LeaveOfAbsence(models.Model):
    """ Leave of absence periods for members. """
    member = models.ForeignKey(Member)
    start = models.DateField()
    end = models.DateField(help_text="Remember!: Editing a Leave of absense directly does not affect member's workshifts.  Please remove them manually from any workshifts that fall within the leave.")
    objects = LeaveOfAbsenceManager()
    


class WorkExemption(models.Model):
    """ Work exemptions for members. """
    type = models.CharField(max_length=1, choices=EXEMPTION_TYPES, default='k')
    member = models.ForeignKey(Member)
    start = models.DateField()
    end = models.DateField()


class AccountManager(models.Manager):
    'Custom manager to add extra methods'
    def active(self):
        return self.filter(accountmember__in=
                           AccountMember.objects.active_depositor()).distinct()

    def inactive(self):
        return self.exclude(accountmember__in=
                            AccountMember.objects.active_depositor())

    def present(self):   # will show up on cash sheets
        return self.filter(accountmember__in=
                           AccountMember.objects.present_depositor()).distinct()

class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    #contact = models.ForeignKey(Member, related_name='contact_for')
    members = models.ManyToManyField(Member, related_name='accounts', 
            through='AccountMember')
    can_shop = models.BooleanField(default=True)
    ebt_only = models.BooleanField()
    hours_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # deposit is now known as equity
    deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # balance is updated with each transaction.save()
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    shared_address = models.BooleanField()

    objects = AccountManager()

    def alphanumericname(self):
        return ''.join(c for c in self.name if c in string.letters+string.digits+' ')[:50]

    def active_members(self):
        return Member.objects.filter(accountmember__in=
                self.accountmember_set.active_depositor())

    @property
    def active_member_count(self):
        return self.active_members().count()

    def billable_members(self):
        ''' active depositors MINUS anyone on leave of absence '''
        return Member.objects.filter(accountmember__in=
                self.accountmember_set.present_depositor())

    @property
    def billable_member_count(self):
        return self.billable_members().count()

    @property
    def discount(self):
        # active working members at 10%
        # active nonworking members at 5%
        # LOA members and proxy shoppers not included
        totaldiscount = 0.0
        memberset = self.billable_members()
        if memberset.count() == 0:
            return 0
        for m in memberset:
            if m.work_status != 'n':
                totaldiscount += 10
            else: 
                totaldiscount += 5
        rounded = round(totaldiscount / memberset.count(), 2)
        # no decimals if can be displayed as integer
        return rounded if int(rounded) != rounded else int(rounded)


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

    @models.permalink
    def get_templimit_url(self):
        return ('templimit', [self.id])

    def members_leaveofabsence_set(self):
        return LeaveOfAbsence.objects.filter(member__accounts=self)

    def recent_cashier(self):
        return self.task_set.filter(job__name='Cashier', time__range=(
            today - datetime.timedelta(120), today))
    
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

    def owes_money(self):
        if self.balance > 0:
            return True

    def hours_owed(self):
        if self.hours_balance > 0:
            return True

    def balance_on(self, time):
        newest_trans = self.transaction_set.filter(
                       timestamp__lt=time).order_by('-timestamp')
        if newest_trans.count():
            return newest_trans[0].account_balance

    def days_old(self):
        oldest = self.members.active().aggregate(Min('date_joined')).values()[0]
        if oldest is None:  # in case of no members or other problem
            return -1
        return (datetime.date.today() - oldest).days

    def months_old(self):
        return self.days_old() / 30
        
    def max_allowed_to_owe(self):
        if self.temporarybalancelimit_set.current():
            return self.temporarybalancelimit_set.current()[0].limit
        if self.days_old() >= 180:
            return self.active_member_count * Decimal('25.00')
        else:
            return self.active_member_count * Decimal('5.00')
    max_allowed_balance = property(max_allowed_to_owe)

    def must_pay(self):
        max_allowed_to_owe = self.max_allowed_to_owe()
        if self.balance > max_allowed_to_owe:
            return self.balance - max_allowed_to_owe

    def way_over_limit(self):
        way_limit = 2 * self.max_allowed_to_owe()
        if self.balance > way_limit:
            return self.balance - way_limit

    def must_work(self):
        if self.hours_balance > Decimal('0.03'):
            return self.hours_balance

    def obligations(self):
        obligations = self.billable_member_count
        if not obligations:
            if self.active_member_count:
                return 'ON LEAVE'
            return
        for am in self.accountmember_set.all():
            if (am.member.regular_shift()
                    or (am.member.work_status in 'ecn' and not am.shopper)):
                obligations -= 1
        if obligations:
            return 'NEEDS SHIFT'

    def frozen_flags(self):
        if self.name == 'One-Time Shopper':
            return
        flags = []
        if self.balance > self.max_allowed_to_owe():
            flags.append('MUST PAY')
        if self.hours_balance > Decimal('0.03'):
            flags.append('MUST WORK')
        if not self.can_shop:
            flags.append('CANNOT SHOP')
        obligations = self.billable_member_count
        if not obligations:
            if self.active_member_count:
                flags.append('ON LEAVE')
            else:
                flags.append('ACCOUNT CLOSED')
        satisfactions = self.accountmember_set.filter(
            Q(member__work_status__in='ecn', shopper=False) |
            Q(member__task__time__gte=datetime.date.today())).count()
        if obligations > satisfactions and self.days_old() > 7:
            flags.append('NEEDS SHIFT')
        if self.ebt_only:
            flags.append('EBT Only')
        return flags

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class AccountMemberManager(models.Manager):
    def active_depositor(self):
        return self.filter(shopper=False, member__in=Member.objects.active())

    def present_depositor(self):
        return self.filter(shopper=False, member__in=Member.objects.present())

    def active_shopper(self):
        return self.filter(shopper=True, member__in=Member.objects.active())

    def inactive(self):
        return self.exclude(member__in=Member.objects.active())

class AccountMember(models.Model):
    account = models.ForeignKey(Account)
    member = models.ForeignKey(Member)
    # account_contact displayed as "deposit holder" per shinara's request
    # -- gsf 2009-05-03

    # In retrospect, I think we should assume deposit_holder = not shopper.
    # After we enabled both, we started getting broken cases where 
    # account_contact != not shopper.  --Paul 2009-10-10

    account_contact = models.BooleanField(default=True, verbose_name="deposit holder")
    # primary_account isn't being displayed for now.  not needed according
    # to shinara -- gsf 2009-05-03
    primary_account = models.BooleanField(default=True)
    # is this member just a shopper on the account?
    shopper = models.BooleanField(default=False)

    objects = AccountMemberManager()
    
    def __unicode__(self):
        return u'%s: %s' % (self.account, self.member)

    class Meta:
        ordering = ['account', 'id']
    


class TemporaryBalanceLimitManager(models.Manager):
    def current(self):
        return self.filter(start__lte=today, until__gte=today)

class TemporaryBalanceLimit(models.Model):
    'start and end may not overlap, otherwise result is unpredictable'
    account = models.ForeignKey(Account)
    limit = models.DecimalField(max_digits=5, decimal_places=2)
    start = models.DateField(auto_now_add=True)
    until = models.DateField()

    objects = TemporaryBalanceLimitManager()

    def __unicode__(self):
        return u'%s may owe %s until %s/%s/%s' % (self.account, self.limit, 
            self.until.month, self.until.day, self.until.year)


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

    def fullmailing(self):
        ''' return full mailing address, including name and country if not USA '''
        ret = '%s\n%s' % (self.member, self.address1)
        if self.address2:
            ret += '\n%s' % self.address2
        ret += '\n%s, %s %s' % (self.city, self.state, self.postal_code)
        if self.country != 'USA':
            ret += '\n%s' % self.country
        return ret

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

# this is duplicated in scheduling/models.  duplicated to avoid circular imports.
def daterange(start, end):
    while start < end:
        yield start
        start += datetime.timedelta(1)

# this should be a method on Skill, but it can't be due to circular imports
def members_with_skill(skill):
    return Member.objects.present().filter(
        task__in=skill.trainedbytasks()).distinct()


