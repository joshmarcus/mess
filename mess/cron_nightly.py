#!/usr/bin/python
import datetime
import smtplib
import sys

from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# these imports raise errors if placed before setup_environ(settings)
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

    dancer = loader.get_template('scheduling/emails/dancer.html')
    dancer_subject = loader.get_template(
            'scheduling/emails/dancer_subject.html')
    excused = loader.get_template('scheduling/emails/excused.html')
    excused_subject = loader.get_template(
            'scheduling/emails/excused_subject.html')
    scheduled = loader.get_template('scheduling/emails/scheduled.html')
    scheduled_subject = loader.get_template(
            'scheduling/emails/scheduled_subject.html')

    reminder_tasks = generate_reminder(datetime.date.today()).exclude(
            member__user__email='').distinct()
    for task in reminder_tasks:
        if task.excused:
            message = excused.render(Context({'task':task}))
            subject = excused_subject.render(Context({'task':task}))
        elif task.job.is_dancer:
            message = dancer.render(Context({'task':task}))
            subject = dancer_subject.render(Context({'task':task}))
        else:
            message = scheduled.render(Context({'task':task}))
            subject = scheduled_subject.render(Context({'task':task}))
        try:
            mail.send_mail(subject, message, None, [task.member.user.email])
        except smtplib.SMTPRecipientsRefused, e:
            print "SMTP Error: %s" % e

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
    #send_to = ('anna3lc@gmail.com',)  # for testing...
    # create email with the file as attachment.
    subject = "cashsheet backup %s" % datetime.date.today()
    message = "You are receiving this message because you are marked as mariposa staff in the MESS.  If MESS is down, contact MESS members according to instructions posted on bulletin board.  Then you can open and print the attached file using your web browser.  It contains a cashsheet accurate as of last night, which cashiers can use until MESS is restored."
    message += "\n\n(You may want to set up your email to filter this message so you don't see it in your inbox everyday.)\n\n"
    # send them the file as an attachment.
    email = mail.EmailMessage(subject, message, None, send_to)
    email.attach('cashsheet.html', outfile)
    try:
        email.send()
    except smtplib.SMTPRecipientsRefused, e:
        print "SMTP Error: %s" % e

def main():
    reminder_emails()
    cashsheet_email()

if __name__ == "__main__":
    main()

