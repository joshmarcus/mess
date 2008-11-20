import sys, os
import xlrd
from xlrd import empty_cell
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from scheduling.models import *
from membership.models import *


def makeJobs(sheet):
    'minimally validate and create jobs from sheet rows'
    print "processing %s" % sheet.name

    for i in range(1, sheet.nrows):
        row = sheet.row(i)
        if row[0].ctype != xlrd.XL_CELL_NUMBER:
            print "rejecting row:\n"
            print row
            continue
        job = Job(id = row[0].value, name = row[1].value)
        if row[3].ctype == xlrd.XL_CELL_TEXT:
            job.description = row[3].value
        if row[4].ctype == xlrd.XL_CELL_NUMBER:
            job.type = row[4].value
        if row[5].ctype == xlrd.XL_CELL_NUMBER:
            job.freeze_days = row[5].value
        if row[6].ctype == xlrd.XL_CELL_NUMBER:
            job.hours_multiplier = row[6].value

        job.save()

def makeTasks(sheet):
    'minimally validate and load tasks'
    print "processing %s" % sheet.name

    isoTimeFmt = "%Y-%m-%dT%H:%M"
    
    for i in range(1, sheet.nrows):
        row = sheet.row(i)
        if row[0].ctype != xlrd.XL_CELL_NUMBER:
            print "rejecting row:\n"
            print row
            continue

        job = Job.objects.get(id = row[0].value)
        start = datetime.datetime.strptime(row[1].value, isoTimeFmt)

        task = Task(
                job = job,
                start = start,
                hours = row[3].value,
                recurrence_unit = row[5].value.lower(),
                recurrence_freq = row[6].value,
                )
        try:
            member = Member.objects.get(user__username = row[7].value)
            account = Account.objects.get(name = row[8].value)
            task.member = member
            task.account = account
        except Member.DoesNotExist, Account.DoesNotExist:
            pass

        try:
            task.deadline = datetime.datetime.strptime(row[2].value, isoTimeFmt)
        except:
            pass
        
        print task

def main():
    'Open Workbooks, dispatch to handlers'
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print "useage: %s <xl workbook>" % sys.argv[0]
        return 0
    
    bookname = sys.argv[1]
    print "opening %s\n" % bookname
    book = xlrd.open_workbook(bookname)
    for sheet in book.sheets():
        if sheet.name == u"Jobs":
            makeJobs(sheet)
        if sheet.name.find('Shift Sch') >= 0:
            makeTasks(sheet)

if __name__ == "__main__":
    sys.exit(main())
