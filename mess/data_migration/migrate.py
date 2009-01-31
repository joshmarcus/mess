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

from mess.membership import models
from mess.scheduling import models as s_models

MAXLINES = 20000    # only import first N members for debugging

def prepare_columns(headers):
    '''
    define where to get each data chunk and how to handle it
    '''
    return {
        'account_name': Column(headers, source=0, parser=strip_notes),
        'section': Column(headers, 'Section'),
        'active_members': Column(headers, 'Active Members', parser=int_or_one),
        'has_proxy': Column(headers, 'Proxy Shopper', parser=is_nonspace),
        'account': [
            Column(headers, source=0, parser=strip_notes),
            Column(headers, 'Old Balance', dest='balance'),
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
            Column(headers, source=parse_shift, porter=set_shift),
            ],
        'proxy': [
            Column(headers, 'Proxy Shopper', make_username),
            Column(headers, 'Proxy Shopper', get_first_name, 'user.first_name'),
            Column(headers, 'Proxy Shopper', get_last_name, 'user.last_name'),
            Column(headers, source=generate_pass, dest='user.password'),
            Column(headers, 'Proxy Shopper #', porter=create_phone),
            Column(headers, 0, porter=set_shopper_flag),
#           Column(headers, 'Street Address & Apt / City State / ZIP',
#               porter=split_and_create_address), 
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
        elif self.dest[:5] == 'user.':
            setattr(new_object.user, self.dest[5:], data)
        else:
            setattr(new_object, self.dest, data)


class PortAccount:
    def __init__(self, excel_row, columns):
        self.sec1_row = excel_row
        self.has_removed_sec1_members = False
        self.cells = [Cell(excel_row, column) for column in columns['account']]
        self.members = [
                    [Cell(excel_row, column) for column in columns['member']] ]
        if columns['has_proxy'].fetch_data(excel_row):
            self.members.append(
                    [Cell(excel_row, column) for column in columns['proxy']] )

    def add_sec4_row(self, excel_row, columns):
        if not self.has_removed_sec1_members:
            self.members = []
            self.has_removed_sec1_members = True
        self.members.append( 
                    [Cell(excel_row, column, backup_row=self.sec1_row)
                            for column in columns['member']] )
        if columns['has_proxy'].fetch_data(excel_row):
            self.members.append(
                    [Cell(excel_row, column, backup_row=self.sec1_row)
                            for column in columns['proxy']] )
        
    def migrate(self):
        # accountname shall be the first element of member.cells
        new_account = models.Account.objects.create(name = self.cells[0].data)
        for cell in self.cells:
            cell.migrate(new_account)
        new_account.save()

        for member_cells in self.members:
            # username shall be the first element of member.cells
            # member must be saved first, so phones etc. can be migrated
            # then it will be re-saved later after all its data is migrated
            new_user = create_unique_user(slug = member_cells[0].data)
            new_member = models.Member.objects.create(user = new_user)
            models.AccountMember.objects.create(account=new_account, 
                                                member=new_member)

            for cell in member_cells[1:]:
                cell.migrate(new_member)
            new_member.save()
            new_user.save()


# here is a slew of parser functions, used to parse excel data

def split_notes(actstr):
    ''' try to split things like  "Best Fest NEEDS SHIFT" '''
    # find last lowercase character
    if actstr == '': return '', ''
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

def is_nonspace(a):
    return len(a) > 0 and not a.isspace()

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
    return split_name(a)[0]

def get_last_name(a):
    return split_name(a)[1]

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
    ''' for now, only fixes dates formatted as "June 15, 2008" '''
    try:
        return time.strftime('%Y-%m-%d',time.strptime(d,'"%B %d, %Y"'))
    except:
        return '1902-01-01'

def parse_shift(headers, excel_row, backup_row=None):
    if excel_row[headers.index('Shift Start Time')].value == '':
        return None
    data = {'start':'Shift Start Time',
        'end':'Shift End Time',
        'job':'Shift Job',
        'day':'Shift Day of Week',
        'rotation':'Rotation',
        'notes':'Shift Notes'}
    for key, columnheader in data.iteritems():
        data[key] = excel_row[headers.index(columnheader)].value

    try:
        data['start'] = xlrd.xldate_as_tuple(data['start'],0)[3:]
        data['end'] = xlrd.xldate_as_tuple(data['end'],0)[3:]
        data['hours'] = (data['end'][0] - data['start'][0] + 
                         (data['end'][1] - data['start'][1])/60.0)
        day_number = ['Monday','Tuesday','Wednesday','Thursday',
                      'Friday','Saturday','Sunday'].index(data['day'])
        (data['interval'], offset_weeks) = {
             'A':(4,0), 'B':(4,1), 'C':(4,2), 'D':(4,3),
             'E':(6,0), 'F':(6,1), 'G':(6,2), 'H':(6,3), 'I':(6,4), 'J':(6,5),
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

def create_unique_user(slug, count=0, countstr=''):
    try:
        return User.objects.create(username = slug + countstr)
    except IntegrityError:
        count += 1
        return create_unique_user(slug, count=count, countstr=str(count))

def create_phone(data, new_member):
    if data != '':
        new_member.phones.create(number = data)

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
                postal_code = addr[2].strip()
            )
            return
    # if problem, return entire original string as street
    new_member.addresses.create( address1 = data )

def set_shift(data, new_member):
    if data == None:
        return
    if isinstance(data, basestring):
        print repr('Not inserting shift %s' % data)
        return

    try:
        job = s_models.Job.objects.get(name=data['job'].strip().title())
    except:
        # maybe jobs should just be loose strings to avoid this?
        job = s_models.Job.objects.get(name='Other Job')

    acct = new_member.primary_account()
    new_task = s_models.Task.objects.create(
            time = data['start'], 
            hours = str(data['hours']),  #float->str->dec is silly but required
            job = job,
            member = new_member,
            account = acct,
            note = data['notes'])
    new_task.set_recur_rule('w',data['interval'],None)
    new_task.update_buffer()
    print repr('Inserted shift %s' % data)

def set_shopper_flag(data, new_member):
    accountmember = new_member.accountmember_set.all()[0]
    accountmember.shopper = True
    accountmember.account_contact = False
    accountmember.save()

@transaction.commit_on_success
def main():
    if len(sys.argv) < 2:
        print 'Usage: %s <xl workbook>' % sys.argv[0]
        return 0
    if len(sys.argv) > 2:
        MAXLINES = int(sys.argv[2])

    datafile = xlrd.open_workbook(sys.argv[1])
    datasheet = datafile.sheet_by_index(0)
    headers = [unicode(x.value).strip() for x in datasheet.row(0)]
    columns = prepare_columns(headers)
    accounts = {}
    
    for n in range(1, min(datasheet.nrows, MAXLINES)):
        excel_row = datasheet.row(n) 
        section = columns['section'].fetch_data(excel_row)
        account_name = columns['account_name'].fetch_data(excel_row)
        result = 'loaded row'
        
        if section == '1.0':
            assert account_name not in accounts
            accounts[account_name] = PortAccount(excel_row, columns)
        elif section == '4.0' and account_name in accounts:
            accounts[account_name].add_sec4_row(excel_row, columns)
        else:
            result = 'SKIPPED row'
        print repr('%s %d, section %s, account %s' %
                (result, n, section, account_name))

    print 'Done Reading Input File!'

    for account_name, account in accounts.iteritems():
        account.migrate()
        print repr('Saved account %s' % account_name)

main()
