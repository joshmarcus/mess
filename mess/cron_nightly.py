
#!/usr/bin/python

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

# these imports raise errors if placed before setup_environ(settings)
import datetime
from mess.scheduling import models
from mess.scheduling.views import generate_reminder
from django.template import loader, Context
from django.core.mail import send_mail

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
        send_mail(subject, message, None, [to])

def main():
    reminder_emails()

if __name__ == "__main__":
    main()



