import sys, os
import xlrd
from xlrd import empty_cell

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from scheduling.models import Job


def makeJobs(sheet):
    'minimally validate and create jobs from sheet rows'
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

def main(argv = sys.argv):
    'Open Workbooks, dispatch to handlers'
    bookname = argv[1]
    print "opening %s\n" % bookname
    book = xlrd.open_workbook(bookname)
    jobs_sheet = book.sheet_by_name('Jobs')
    makeJobs(jobs_sheet)
    

if __name__ == "__main__":
    sys.exit(main())
