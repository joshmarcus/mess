import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

import xlrd
from xlrd import empty_cell
import datetime
from dateutil.parser import parse

from scheduling import models as sm
from membership import models as mm


def make_job(row, book):
    'minimally validate and create jobs from sheet rows'
    if row[0].ctype != xlrd.XL_CELL_NUMBER:
        return
    job = sm.Job(id = row[0].value, name = row[1].value)
    if row[3].ctype == xlrd.XL_CELL_TEXT:
        job.description = row[3].value
    if row[4].ctype == xlrd.XL_CELL_NUMBER:
        job.type = row[4].value
    if row[5].ctype == xlrd.XL_CELL_NUMBER:
        job.freeze_days = row[5].value
    if row[6].ctype == xlrd.XL_CELL_NUMBER:
        job.hours_multiplier = row[6].value

    job.save()
    print job

# if columns were addressable by label, this would collapse easily with the other func
def make_task_fmt2(row, book):
    'minimally validate and load format 2 tasks'
    isoTimeFmt = "%Y-%m-%dT%H:%M"
    
    if row[0].ctype != xlrd.XL_CELL_NUMBER:
        return

    if row[1].ctype != xlrd.XL_CELL_DATE:
        print "format 2 handler got format 1 row" 
        return

    job = sm.Job.objects.get(id = row[0].value)

    start_day = datetime.datetime(*xlrd.xldate_as_tuple(row[1].value, book.datemode))

    if row[2].ctype == xlrd.XL_CELL_DATE:
        start_time_tup = xlrd.xldate_as_tuple(row[2].value, book.datemode)
        start_time = datetime.time(*start_time_tup[3:]) #slice out just the time part
    else:
        start_time = parse(row[2].value).time()
    
    start = datetime.datetime.combine(start_day, start_time)

    task = sm.Task(
            job = job,
            time = start,
            hours = str(row[4].value),
            frequency = row[6].value.lower(),
            interval = row[7].value,
            )

    acct_name = row[9].value
    mem_name = row[8].value
    if acct_name != "tba" and acct_name != "tbd" and acct_name != "TBD" and acct_name != "":
        try:
            account = mm.Account.objects.get(name = acct_name)
        except mm.Account.DoesNotExist, e:
            e.account = acct_name
            raise e
        members = account.members.filter(user__first_name = mem_name)
        if members.count() == 0:
            e = mm.Member.DoesNotExist()
            e.account = str(account)
            e.member = mem_name
            raise e
        task.member = members[0]
        task.account = account
    
    task.save()
#    print task

def make_task_fmt1(row, book):
    'minimally validate and load format 1 tasks'
    isoTimeFmt = "%Y-%m-%dT%H:%M"
    
    if row[0].ctype != xlrd.XL_CELL_NUMBER:
        return

    if row[1].ctype != xlrd.XL_CELL_TEXT:
        print "format 1 handler got format 2 row" 
        return

    job = sm.Job.objects.get(id = row[0].value)
    start = datetime.datetime.strptime(row[1].value, isoTimeFmt)

    task = sm.Task(
            job = job,
            time = start,
            hours = str(row[3].value),
            frequency = row[5].value.lower(),
            interval = row[6].value,
            )
    acct_name = row[8].value
    mem_name = row[7].value
    if acct_name != "tba" and acct_name != "tbd" and acct_name != "TBD" and acct_name != "":
        try:
            account = mm.Account.objects.get(name = acct_name)
        except mm.Account.DoesNotExist, e:
            e.account = acct_name
            raise e
        members = account.members.filter(user__first_name = mem_name)
        if members.count() == 0:
            e = mm.Member.DoesNotExist()
            e.account = str(account)
            e.member = mem_name
            raise e
        task.member = members[0]
        task.account = account
    
    task.save()
#    print task

def dispatch_rows(sheet, book):
    print "processing %s\n\n" % sheet.name
        
    if sheet.name == u'Jobs':
        handler = make_job
    if sheet.name.find('Shift Sch') >= 0:
        if sheet.name.find('Fmt1') >= 0:
            handler = make_task_fmt1
        else:
            handler = make_task_fmt2

    for i in range(1, sheet.nrows):
        row_idx = i + 1
        try:
            row = sheet.row(i)
            handler(row, book)
        except sm.Job.DoesNotExist, e:
            print "FATAL  %s: Sheet %s, row %d\n" % (e, sheet.name, row_idx)
        except sm.Account.DoesNotExist, e:
            print "Partial  Unknown account %s: Sheet %s, row %d\n" % (e.account, sheet.name, row_idx)
        except sm.Member.DoesNotExist, e:
            print "Partial  No member %s in account %s: Sheet %s, row %d\n" % (e.member, e.account, sheet.name, row_idx)
        except:
            print "TOTAL FAIL!!! Sheet %s, row %d\n" % (sheet.name, row_idx)
            raise

def main():
    'Open Workbooks, dispatch to handlers'
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print "usage: %s <xl workbook>" % sys.argv[0]
        return 0
    
    bookname = sys.argv[1]
    print "opening %s\n" % bookname
    book = xlrd.open_workbook(bookname)
    for sheet in book.sheets():
        dispatch_rows(sheet, book)

if __name__ == "__main__":
    sys.exit(main())
