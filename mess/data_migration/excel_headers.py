import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

import xlrd

databook = xlrd.open_workbook(sys.argv[1])
for header in databook.sheet_by_index(0).row(0):
    print header.value
