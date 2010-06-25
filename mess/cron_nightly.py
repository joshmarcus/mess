
#!/usr/bin/python

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# these imports raise errors if placed before setup_environ(settings)
import datetime
from django.shortcuts import render_to_response
from mess.scheduling import models
from mess.scheduling.views import generate_reminder
from mess.accounting.views import cashsheet
from mess.accounting import forms as a_forms
from mess.membership import models as m_models
from django.template import loader, Context
from django.core import mail

def reminder_emails():
    '''
    there is no later, paul, there is only now.
    here is some code to send REMINDER EMAILS!
    '''
    print "***********************************"
    print "sending email reminders on %s" % datetime.date.today()
    print "***********************************"

    reminder_tasks = generate_reminder(datetime.date.today()).exclude(
            member__user__email='').distinct()

    message_template = loader.get_template('scheduling/reminder_mail.html')
    for task in (reminder_tasks):
        message = message_template.render(Context({'task':task}))
        # now have to split to: and subject: off of those lines to send them to mail
        print message #piped to /var/log/mess.log
        (to, subject, message) = message.split('\n', 2)
        to = to.split(' ', 1)[1]
        subject = subject.split(' ', 1)[1]
        mail.send_mail(subject, message, None, [to])

def cashsheet_email():
    '''
    bundles cash sheet report with its print css, then emails it to all staff.
    '''
    # some code copied from accounting views
    form = a_forms.CashSheetFormatForm()
    row_height = 2.5
    rows_per_page = 22
    # include ! accounts at top ("Mariposa" and "UNCLAIMED")
    accounts = (list(m_models.Account.objects.filter(name__startswith='!')) +
                list(m_models.Account.objects.present()))
    outfile = render_to_response('accounting/cashsheet_email.html', locals())

    # get staff email addresses.
    send_to = m_models.Member.objects.filter(user__is_staff=True).values_list('user__email', flat=True)
#    send_to = ('anna3lc@gmail.com',)  # for testing...
    # create email with the file as attachment.
    subject = "cashsheet backup %s" % datetime.date.today()
    message = "You are receiving this message because you are marked as mariposa staff in the MESS.  If MESS is down, contact MESS members according to instructions posted on bulletin board.  Then you can open and print the attached file using your web browser.  It contains a cashsheet accurate as of last night, which cashiers can use until MESS is restored."
    message += "\n\n(You may want to set up your email to filter this message so you don't see it in your inbox everyday.)\n\n"
    # send them the file as an attachment.
    email = mail.EmailMessage(subject, message, None, send_to)
    email.attach('cashsheet.html', outfile)
    email.send()

def main():
    reminder_emails()
    cashsheet_email()

if __name__ == "__main__":
    main()



