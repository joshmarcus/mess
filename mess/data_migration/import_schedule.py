import sys
import codecs
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

import xlrd
from xlrd import empty_cell
import datetime
from dateutil.parser import parse
from django.db import transaction


from scheduling import models as sm
from membership import models as mm

def zip_row(row, headers):
    rowItems = [col for col in row]
    return dict(zip(headers, rowItems))

class DateParseError(Exception):
    pass


def make_job(row, zipRow, book):
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

def get_start_time1(row, zipRow, book):
    isoTimeFmt = "%Y-%m-%dT%H:%M"
    try:
        start = datetime.datetime.strptime(row[1].value, isoTimeFmt)
    except:
        e = DateParseError()
        e.time = row[1].value
        raise e
    return start

def get_start_time2(row, zipRow, book):
    start_day = datetime.datetime(*xlrd.xldate_as_tuple(row[1].value, book.datemode))
    try:
        if row[2].ctype == xlrd.XL_CELL_DATE:
            start_time_tup = xlrd.xldate_as_tuple(row[2].value, book.datemode)
            start_time = datetime.time(*start_time_tup[3:]) #slice out just the time part
        else:
            start_time = parse(row[2].value).time()
    except:
        e = DateParseError()
        e.time = row[2].value
        raise e

    start = datetime.datetime.combine(start_day, start_time)
    return start

def make_task(row, zipRow, book):
    if row[0].ctype != xlrd.XL_CELL_NUMBER:
        return

    if row[1].ctype == xlrd.XL_CELL_DATE:
        start_func = get_start_time2
    else:
        start_func = get_start_time1


    recur_rule = sm.RecurRule(
            frequency = zipRow["d/w/mo"].value.lower(),
            interval = zipRow["Cycle"].value,
    )
    recur_rule.save()

    task = sm.Task(
            job = sm.Job.objects.get(id = zipRow["FK-Job"].value),
            time = start_func(row, zipRow, book),
            hours = str(zipRow["Hrs"].value),
            recur_rule = recur_rule,
    )
    task.save()

    acct_name = zipRow["Account"].value.strip()
    mem_name = zipRow["Member Name"].value.strip()
    if acct_name != "tba" and acct_name.lower() != "tbd" and acct_name.lower() != "t-b-d" and acct_name != "":
        try:
            account = mm.Account.objects.get(name = acct_name)
        except mm.Account.DoesNotExist, e:
            e.account = acct_name
            raise e
        members = account.members.filter(user__first_name = mem_name)
        if members.count() == 0:
            members = account.members.filter(user__first_name__startswith = mem_name)
        if members.count() == 0:
            e = mm.Member.DoesNotExist()
            e.account = str(account)
            e.member = mem_name
            raise e
        worker = sm.Worker(
                task = task,
                member = members[0],
                account = account,
        )
        worker.save()
    
@transaction.commit_on_success
def dispatch_rows(sheet, book):
    print "processing %s\n\n" % sheet.name
    errors = 0
    if sheet.name == u'Jobs':
        handler = make_job
    elif sheet.name.find('Shift Sch') >= 0:
        handler = make_task
    else:
        print "Aborting %s: Unknown sheet type" % sheet.name
        return errors
        
    header_row = sheet.row(0)
    headers = [str(col.value) for col in header_row]

    for i in range(1, sheet.nrows):
        row_idx = i + 1
        try:
            row = sheet.row(i)
            zipRow = zip_row(row, headers)
            handler(row, zipRow, book)
        except sm.Job.DoesNotExist, e:
            errors += 1
            print "FATAL  %s: Sheet %s, row %d\n" % (e, sheet.name, row_idx)
        except DateParseError, e:
            errors += 1
            print "FATAL  can't parse time %s: Sheet %s, row %d\n" % (e.time, sheet.name, row_idx)
        except sm.Account.DoesNotExist, e:
            errors += 1
            print "Partial  Unknown account '%s': Sheet %s, row %d\n" % (e.account, sheet.name, row_idx)
        except sm.Member.DoesNotExist, e:
            errors += 1
            print "Partial  No member '%s' in account '%s': Sheet %s, row %d\n" % (e.member, e.account, sheet.name, row_idx)
        except:
            print "TOTAL FAIL!!! Sheet %s, row %d\n" % (sheet.name, row_idx)
            raise
    return errors

def main():
    'Open Workbooks, dispatch to handlers'
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print "usage: %s <xl workbook>" % sys.argv[0]
        return 0
    
    bookname = sys.argv[1]
    print "opening %s\n" % bookname
    book = xlrd.open_workbook(bookname)
    errors = 0
    for sheet in book.sheets():
        errors += dispatch_rows(sheet, book)
    print "Total import errors: %d" % errors

if __name__ == "__main__":
    sys.exit(main())
