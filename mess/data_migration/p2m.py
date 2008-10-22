# execute from mess/ directory
# for merging profiles into membership

from django.core.management import setup_environ
import settings

setup_environ(settings)

from membership import models as m_models
from profiles import models as p_models

profiles = p_models.UserProfile.objects.all()

for profile in profiles:
    print "Processing %s" % profile.user
    member = m_models.Member.objects.get(user=profile.user)
    for address in profile.addresses.all():
        member.addresses.add(address)
    for phone in profile.phones.all():
        member.phones.add(phone)
    for email in profile.emails.all():
        member.emails.add(email)
