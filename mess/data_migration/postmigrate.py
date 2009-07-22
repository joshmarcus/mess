#!/usr/bin/python

# This script is intended to populate the MESS Database for the first time.
# 
# Currently this script only imports members in Section 1.0 (active) and 
# Section 4.0 (multi-member information).  All other sections are SKIPPED.
#
# Beware: Some accounts get imported incorrectly, and must be fixed
# by hand after importing.
#
# You probably want to remove all fixtures before you run this...
import pdb

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# these imports raise errors if placed before setup_environ(settings)
import string
import time
import datetime
import re
import xlrd
from random import choice
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q

from mess.membership import models
from mess.scheduling import models as s_models


def prepare_columns(headers):
    '''
    define where to get each data chunk and how to handle it
    '''
    return {
        'account_name': Column(headers, source=0, parser=strip_notes),
        'section': Column(headers, 'Section'),
        'active_members': Column(headers, 'Active Members', parser=int_or_one),
        'has_proxy': Column(headers, 'Proxy Shopper', parser=is_not_none),
        'account': [
            Column(headers, source=0, parser=strip_notes),
            Column(headers, 'Old Balance', parser=or_zero, dest='balance'),
            Column(headers, source=get_all_notes, dest='note'),
            Column(headers, 'Hours Balance', parser=or_zero, dest='hours_balance'),
            Column(headers, 'Cumulative deposit', parser=or_zero, dest='deposit'),
            ],
        'member': [
            Column(headers, 'Primary Member', make_username),
            Column(headers, 'Primary Member', get_first_name, 'user.first_name'),
            Column(headers, 'Primary Member', get_last_name, 'user.last_name'),
            Column(headers, source=generate_pass, dest='user.password'),
            Column(headers, 'Join Date', date_format, 'date_joined'),
            Column(headers, 'Has key?', is_yes, 'has_key'),
            Column(headers, 'phone #', porter=create_phone),
            Column(headers, 'second phone #', porter=create_phone),
            Column(headers, 'email', porter=create_email),
            Column(headers, 'Street Address & Apt / City State / ZIP',
                porter=split_and_create_address), 
            Column(headers, source=get_section, porter=set_section_flag),
            Column(headers, source=get_all_notes, porter=add_account_note),
            Column(headers, source=parse_shift, porter=set_shift),
            Column(headers, source=get_work_hist, porter=set_work_hist),
            ],
        'proxy': [
            Column(headers, 'Proxy Shopper', make_username),
            Column(headers, 'Proxy Shopper', get_first_name, 'user.first_name'),
            Column(headers, 'Proxy Shopper', get_last_name, 'user.last_name'),
            Column(headers, source=generate_pass, dest='user.password'),
            Column(headers, 'Proxy Shopper #', porter=create_phone),
            Column(headers, 'phone #', porter=create_phone),
            Column(headers, source=get_section, porter=set_section_flag),
            Column(headers, source=parse_shift_for_proxy, porter=set_shift),
            Column(headers, 0, porter=set_shopper_flag),
            ],
        'account_post': [
            Column(headers, 'Old Balance', parser=or_zero, dest='balance'),
            Column(headers, 'Hours Balance', parser=or_zero, dest='hours_balance'),
            Column(headers, 'Cumulative deposit', parser=or_zero, dest='deposit'),
            Column(headers, 'Active Members', porter=am_compare_and_warn),
            ],
        'member_post': [
            Column(headers, 'Join Date', date_format, 'date_joined'),
            ] }

class Cell:
    ''' 
    roughly, each excel cell gets one of these
    specifically, each row has one of these for each Column, as per below
    so the 100,000 cell objects will each point to one of 100 column objects
    '''
    def __init__(self, excel_row, column, backup_row=None):
        self.column = column
        self.data = column.fetch_data(excel_row, backup_row=backup_row)

    def migrate(self, new_object):
        self.column.migrate(self.data, new_object)

class Column:
    ''' 
    roughly, each excel column gets one of these,
    in which case 'source' is normally the header like 'Join Date'

    however, a Column object can grab data from various excel columns by
    specifying a 'source' function.  For example, 'notes' could be a Column
    that finds 'notes' data scattered across each row.
    '''
    def __init__(self, headers, source, parser=None, dest=None, porter=None):
        self.parser = parser
        self.dest = dest
        self.source_fn = None
        if isinstance(source, basestring):
            try:
                self.source_col = headers.index(source)
            except ValueError:
                print 'ERROR: Cannot find excel column "%s".' % source
                raise
        elif callable(source):
            self.source_fn = source
            self.headers = headers
        else:
            self.source_col = int(source)
        if porter:
            self.migrate = porter

    def fetch_data(self, excel_row, backup_row=None):
        if self.source_fn:
            return self.source_fn(self.headers, excel_row, backup_row)
        val = unicode(excel_row[self.source_col].value).strip()
        if (val == '' or val.isspace()) and backup_row:
            val = unicode(backup_row[self.source_col].value).strip()
        if self.parser:
            return self.parser(val)
        else:
            return val

    def migrate(self, data, new_object):
        if self.dest == None:
            # should perhaps annotate that we're throwing data away...
            pass
        elif data == None:
            return
        elif self.dest[:5] == 'user.':
            olddata = getattr(new_object.user, self.dest[5:])
            setattr(new_object.user, self.dest[5:], data)
            newdata = getattr(new_object.user, self.dest[5:])
        else:
            olddata = getattr(new_object, self.dest)
            setattr(new_object, self.dest, data)
            newdata = getattr(new_object, self.dest)
        if olddata == newdata:
            print 'verified data %s = %s ' % (self.dest, repr(data))
        else:
            try:
                if float(olddata) == float(newdata):
                    print 'verified data %s = %s ' % (self.dest, repr(data))
                else:
                    print 'UPDATED DATA %s = %s ' % (self.dest, repr(data))
            except:
                print 'UPDATED DATA %s = %s ' % (self.dest, repr(data))


# here is a slew of parser functions, used to parse excel data

def split_notes(actstr):
    ''' try to split things like  "Best Fest NEEDS SHIFT" '''
    if actstr == '': 
        return '', ''
    # don't split if it's a final uppercase letter like Madame K
    if len(actstr) >= 2 and actstr[-1] in string.uppercase and actstr[-2] == ' ':
        return actstr.strip(), ''
    # find last lowercase character
    s = len(actstr) - 1
    while s >= 0 and actstr[s] not in unicode(string.lowercase):
        s -= 1
    while s < len(actstr) and actstr[s] not in unicode(string.whitespace):
        s += 1
    if s == len(actstr) - 1: return actstr.strip(), ''
    return actstr[:s].strip(), actstr[s:].strip()

def strip_notes(a):
    return split_notes(a)[0]

def int_or_one(a):
    try:
        return int(a)
    except:
        return 1

def or_zero(a):
    try:
        test_float = float(a)
        return a
    except:
        return 0

def is_not_none(a):
    return len(a) > 0 and not a.isspace() and a.lower() != 'none'

def is_yes(a):
    return a.lower() == 'yes'

def split_name(namestring):
    names = namestring.strip().rsplit(None,1)
    if len(names) == 0:
        return 'Firstname', 'Lastname'
    if len(names) == 1:
        return names[0], 'Lastname'
    return names[0], names[1]

def get_first_name(a):
    return split_name(a)[0][:30]

def get_last_name(a):
    return split_name(a)[1][:30]

def make_username(a):
    alpha_not = re.compile(r'\W')
    ret = alpha_not.sub('', a).lower()[:8]
    if ret == '':
        return 'blanknam'
    return ret

def generate_pass(headers, arguments_are_ignored, backup_row=None):
    # this just disables login.  Real password must use 'algo$salt$hash'
    return ''.join([choice(string.letters+string.digits) for i in range(8)])

def date_format(d):
    if d == '':
        return None # '1903-01-01'
    try:
        ret = datetime.date(*xlrd.xldate_as_tuple(float(d),0)[:3])
        print 'parsed date: %s' % ret
        return ret
    except:
        pass
    try:
        return datetime.date(*time.strptime(d,'"%B %d, %Y"')[:3])
    except:
        return None # '1902-01-01'

def get_all_notes(headers, excel_row, backup_row=None):
    # start with notes in the Accountname field (column 0)
    note = [split_notes(unicode(excel_row[0].value))[1]] 
    for excel_field in ['Shift Notes', 'Shift Start Time Notes', 'SKILLS', 
            'Acct Closing Notes', 
            'Contact History', 'EXEMPTION NOTES/EXPIRY', 'Notes', 
            'workshift Notes']:
        new_note = unicode(excel_row[headers.index(excel_field)].value).strip()
        if new_note != '':
            note.append(excel_field + ': ' + new_note)
    return '\n'.join(note)
    
def parse_shift_for_proxy(headers, excel_row, backup_row=None):
    return parse_shift(headers, excel_row, backup_row=None, shift_for_proxy=True)

def proxy_steals_shift(headers, excel_row):
    workshift_member_name = str(excel_row[headers.index('Work shift member Name')].value).strip().lower()
    proxy_name = str(excel_row[headers.index('Proxy Shopper')].value).strip().lower()
    if len(workshift_member_name) > 0 and len(proxy_name) > 0 and workshift_member_name[:4] == proxy_name[:4]:
        print 'Proxy Steals Shift!! ' + proxy_name + workshift_member_name
        return True
    else:
        return False

def parse_shift(headers, excel_row, backup_row=None, shift_for_proxy=False):
    if proxy_steals_shift(headers, excel_row) != shift_for_proxy:
        return None
#   if excel_row[headers.index('Shift Start Time')].value == '':
#       return None
    data = {'start':'Shift Start Time',
        'end':'Shift End Time',
        'job':'Shift Job',
        'day':'Shift Day of Week',
        'rotation':'Rotation',}
#       'notes':'Shift Notes'}
    for key, columnheader in data.iteritems():
        data[key] = excel_row[headers.index(columnheader)].value

    DEADLINE_JOBS = ['Recycling','Cheese Cutter','Cleaner/Bath','Cleaner']
    try:
        if data['job'] in DEADLINE_JOBS:
            data['start'] = (23,59,0)
            data['hours'] = 2
        elif data['job'].upper() == 'DANCER':
            data['start'] = (23,55,0)
            data['hours'] = 2
            data['day'] = 'Sunday'
        else:
            data['start'] = xlrd.xldate_as_tuple(data['start'],0)[3:]
            data['end'] = xlrd.xldate_as_tuple(data['end'],0)[3:]
            data['hours'] = (data['end'][0] - data['start'][0] + 
                             (data['end'][1] - data['start'][1])/60.0)
        day_number = ['Monday','Tuesday','Wednesday','Thursday',
                      'Friday','Saturday','Sunday'].index(data['day'])
        (data['interval'], offset_weeks) = {
             'A':(4,0+4), 'B':(4,1), 'C':(4,2), 'D':(4,3),
             'E':(6,0+6), 'F':(6,1), 'G':(6,2), 'H':(6,3), 'I':(6,4), 'J':(6,5),
             }[data['rotation']]
        ROTATION_START = (2009,1,26)
        data['start'] = (datetime.datetime(*(ROTATION_START + 
                                                   data['start']))  
                   + datetime.timedelta(weeks=offset_weeks, days=day_number))
        print 'Successful shift import %(day)s %(rotation)s %(job)s' % data
        return data
    except:
        print 'Failed shift import %(day)s %(rotation)s %(job)s' % data
        return ' '.join([str(x) for x in data.values()])

        

# and here is a slew of porter functions, used to migrate data into the db

def am_compare_and_warn(excel_active_members, mess_account):
    try:
        xam = int(float(excel_active_members))
    except ValueError:
        print 'could not parse active member count %s' % excel_active_members
        return
    mam = mess_account.active_member_count
    if xam == mam:
        print 'verified %s active members' % xam
    elif mam > 0:
        print 'NOT EQUAL: %s has %s active members in Excel, %s in MESS' % (
                mess_account.name, xam, mam)

def create_unique_user(slug, count=0, countstr=''):
    username = slug + countstr
    if User.objects.filter(username=username):
        count += 1
        return create_unique_user(slug, count=count, countstr=str(count))
    return User.objects.create(username=username)

def create_phone(data, new_member):
    if data != '':
        new_member.phones.create(number=data[:20])

def create_email(data, new_member):
    if data != '':
        new_member.emails.create(email = data)

def split_and_create_address(data, new_member):
    if data == '':
        return
    addr = data.rsplit('/',2)
    if len(addr) == 3:
        citystate = addr[1].strip().rsplit(None, 1)
        if len(citystate) == 2:
            new_member.addresses.create(
                address1 = addr[0].strip(),
                city = citystate[0].strip(),
                state = citystate[1].strip(),
                postal_code = addr[2].strip()[:20],
            )
            return
    # if problem, return entire original string as street
    new_member.addresses.create( address1 = data )

def add_account_note(data, new_member):
    ''' called for every member, but this function mostly acts for sec4 '''
    acct = new_member.primary_account()
    if data in acct.note:    # for sec1 notes which are already in
        return
    if acct.note != '':
        acct.note += '\n'
    acct.note += new_member.user.get_full_name() + ': ' + data
    acct.save()

def set_shift(data, new_member):
    if data == None:
        return
    if isinstance(data, basestring):
        if data == '' or data.isspace():
            print 'Not inserting blank shift.'
            return
        elif 'EXEMPT' in data.upper():
            new_member.work_status = 'e'
        elif ('COMMITTEE' in data.upper() or 'FARM' in data.upper() 
                or 'FACILITATOR' in data.upper() or 'SCRIBE' in data.upper()
                or 'NEWSLETTER' in data.upper() or 'BUSINESS' in data.upper()
                or 'ORIENTATION' in data.upper() or 'TOOL' in data.upper()):
            new_member.work_status = 'c'
        else:
            print 'Problem importing shift...'
        add_account_note('Shift info: '+data, new_member)
        print repr('Inserting shift as note: %s' % data)
        return
    try:
        job = s_models.Job.objects.get(name=data['job'].strip().title())
    except:
        add_account_note('Shift job not in list: '+data['job'], new_member)
        # maybe jobs should just be loose strings to avoid this?
        job = s_models.Job.objects.get(name='Other Job')

    acct = new_member.primary_account()
    new_task = s_models.Task.objects.create(
            time = data['start'], 
            hours = str(data['hours']),  #float->str->dec is silly but required
            job = job,
#           note = data['notes'],
            member = new_member,
            account = acct)
    new_task.set_recur_rule('w',data['interval'],None)
    new_task.update_buffer()
    print repr('Inserted shift %s' % data)

def set_shopper_flag(data, new_member):
    accountmember = new_member.accountmember_set.all()[0]
    accountmember.shopper = True
    accountmember.account_contact = False
    accountmember.save()

def get_section(headers, excel_row, backup_row=None):
    if str(excel_row[headers.index('Section')].value) == '3.0' and \
            'LOA' in str(excel_row[0].value):
        return 'LOA'
    else:
        return str(excel_row[headers.index('Section')].value)

def set_section_flag(data, new_member):
    if data == 'LOA':
        new_member.status = 'L'
    elif data == '3.0':
        new_member.status = 'm' # missing
    elif data == '3.5':
        new_member.status = 'x' # missing delinquent?
    elif data == '5.0':
        acct = new_member.primary_account()
        acct.ebt_only = True
        acct.save()
    elif data == '6.0':
        new_member.status = 'd' #departed
    print 'new_member.status is %s because data was %s' % (new_member.status, data)

def get_work_hist(headers, excel_row, backup_row=None):
    hist = []
    event_re = re.compile('([0-9]{1,2})/([0-9]{1,2})/?([YEMUB]{1,2})([0-9.]*)')
    for header in headers:
        if header[:14] != '2008Attendance' and header[:14] != '2009Attendance':
            continue
        if excel_row[headers.index(header)].value == '':
            continue
        for event in str(excel_row[headers.index(header)].value).split():
            try:
                (month,date,flags,hours) = event_re.match(event).group(1,2,3,4)
                month = int(month)
                date = int(date)
                if flags == 'M':
                    flags = 'YM'
                year = int(header[:4])
                if hours == '':
                    hours = '2'
                if month == 1 and header[:16] == '2008Attendance12':
                    year = 2009
                task = {'date': datetime.datetime(year,month,date,0,1,0),
                        'hours': float(hours),
                        'excused': 'E' in flags,
                        'makeup': 'M' in flags,
                        'banked': 'B' in flags,
                        'hours_worked': float(hours)*('Y' in flags) }
                assert 'Y' in flags or 'E' in flags or 'U' in flags
                hist.append(task)
            except:
                print 'Cannot parse work history event: '+event
    return hist

def set_work_hist(data, new_member):
    job = s_models.Job.objects.get(name='Other Job')
    acct = new_member.primary_account()
    for hist in data:
        new_task = s_models.Task.objects.create(
            time = hist['date'],
            hours = str(hist['hours']),  #float->str->dec is silly but required
            hours_worked = str(hist['hours_worked']),
            excused = hist['excused'],
            makeup = hist['makeup'],
            banked = hist['banked'],
            job = job,
            member = new_member,
            account = acct)


def heuristic_get_member(excel_row, columns, account):
    slugname = columns['member'][0].fetch_data(excel_row)
    try:
        return account.members.get(user__username__icontains=slugname)
    except (models.Member.DoesNotExist, models.Member.MultipleObjectsReturned):
        pass
    if slugname == 'blanknam' and account.members.count() == 1:
        return account.members.all()[0]
    try:
        firstname = columns['member'][1].fetch_data(excel_row)
        lastname = columns['member'][2].fetch_data(excel_row)
        return account.members.get(Q(user__first_name__icontains=firstname) | Q(user__last_name__icontains=lastname))
    except models.Member.DoesNotExist:
        if slugname == 'blanknam':
            return 'WARNING member not gotten %s %s %s' % (slugname, firstname, lastname)
        elif account.members.count() == 0:
            return 'WARNING account no members (%s %s %s)' % (slugname, firstname, lastname)
        else:
            return 'MEMBER NOT GOTTEN %s %s %s' % (slugname, firstname, lastname)
    except models.Member.MultipleObjectsReturned:
        return 'MEMBER NOT GOTTEN %s %s %s -- MULTIPLE' % (slugname, firstname, lastname)

def heuristic_get_account(account_name):
    try:
        return models.Account.objects.get(name__iexact=account_name)
    except models.Account.MultipleObjectsReturned:
        return 'ACCOUNT NOT GOTTEN AS %s -- MULTIPLE' % account_name
    except models.Account.DoesNotExist:
        try:
            acct = models.Account.objects.get(name__istartswith=account_name)
            print repr('WARNING NOT EXACT %s as %s' % (account_name, acct.name))
            return acct
        except models.Account.MultipleObjectsReturned:
            return 'ACCOUNT NOT GOTTEN STARTSWITH %s -- MULTIPLE' % account_name
        except models.Account.DoesNotExist:
            return 'ACCOUNT NOT GOTTEN STARTSWITH %s' % account_name

def postmigrate(excel_row, columns, account_name, section, foundaccts):
    if account_name == '':
        return 'SKIPPED'
    if section not in ['1.0','3.0','3.5','4.0','5.0','6.0']:
        return 'SKIPPED'

    account = heuristic_get_account(account_name)
    if isinstance(account, basestring):  # error returned as string
        return account
    if account in foundaccts and foundaccts[account] == True:
        return 'OOPS!  ALREADY MIGRATED ACCOUNT'
    if account in foundaccts:
        foundaccts[account] = True

    for column in columns['account_post']:
        Cell(excel_row, column).migrate(account)
    account.save()
    print repr('saved account %s...' % account_name)

    member = heuristic_get_member(excel_row, columns, account)
    if isinstance(member, basestring):   # error returned as string
        return member

    for column in columns['member_post']:
        Cell(excel_row, column).migrate(member)
    member.save()
    return 'saved member %s...' % member.user.username


@transaction.commit_on_success
def main():
    if len(sys.argv) < 2:
        print 'Usage: %s <xl workbook>' % sys.argv[0]
        return 0

    datafile = xlrd.open_workbook(sys.argv[1])
    datasheet = datafile.sheet_by_index(0)
    headers = [unicode(x.value).strip() for x in datasheet.row(0)]
    columns = prepare_columns(headers)

    if len(sys.argv) > 2:   # limit members for debugging
        rows_to_import = min(datasheet.nrows, int(sys.argv[2]))
    else:
        rows_to_import = datasheet.nrows
    
    # keep track of which existing accounts were postmigrated
    foundaccts = dict([(x,False) for x in models.Account.objects.active()])
    for n in range(1, rows_to_import):
        excel_row = datasheet.row(n) 
        section = columns['section'].fetch_data(excel_row)
        account_name = columns['account_name'].fetch_data(excel_row)
        result = postmigrate(excel_row, columns, account_name, section, foundaccts)
        print repr('%s section %s, row %d, account %s' %  
                (result, section, n, account_name))

    for acct, wasfound in foundaccts.iteritems():
        if not wasfound:
            print repr('MESS active account %s was NOT FOUND in the input.' % 
                    acct.name)

main()
