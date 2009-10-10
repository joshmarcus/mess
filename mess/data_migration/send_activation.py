
from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.contrib.auth import forms as auth_forms
from mess.membership import models

def main():
    activemems = models.Member.objects.active_not_LOA()
    # change the filter to send chunks at a time, organized by last name
    targetmems = activemems.filter(user__last_name__gt='M')
    targetusers = [mem.user for mem in targetmems]
    for u in targetusers:
        print u, u.first_name, u.last_name
        if '$' in u.password:
            print '...already has a password...sending reset anyway.'
        if u.email == '':
            if u.get_profile().emails.all().count() == 0:
                print '...has no email at all'
                continue
            u.email = u.get_profile().emails.all()[0].email
            u.save()
            print '...saved email address %s' % u.email
        try:
            phantomform = auth_forms.PasswordResetForm({'email':u.email})
            assert phantomform.is_valid()
            phantomform.save(use_https=True, 
                email_template_name='membership/welcome_email.txt')
            print '...sent reset email to %s' % u.email
        except:
            print '...had SOME kind of bad error...'

main()

