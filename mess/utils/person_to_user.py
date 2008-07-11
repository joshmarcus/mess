"""
person_to_user.py creates a username from a person's name, creates the user,
and links the person to it.  
"""
import re
import string
from random import choice
from sqlite3 import IntegrityError

import sys
sys.path.insert(0, '/home/gsf/svn')

from django.core.management import setup_environ
from mess import settings
setup_environ(settings)

from mess.people.models import Person
from django.contrib.auth.models import User, Group

alpha_not = re.compile(r'\W')
def slug_name(name):
    alpha = alpha_not.sub('', name)
    lowered = alpha.lower()
    if len(lowered) > 8:
        sliced = lowered[:8]
    else:
        sliced = lowered
    return sliced

def generate_pass():
    return ''.join([choice(string.letters+string.digits) for i in range(8)])

def save_user(user, slug, count):
    try:
        user.save()
    except IntegrityError:
        new_name = slug + str(count)
        user.username = new_name
        count += 1
        save_user(user, slug, count)

member_group = Group.objects.get(id=1)
# wrap in list because of http://code.djangoproject.com/ticket/7411
persons = list(Person.objects.all())
for person in persons:
    slug = slug_name(person.name)
    password = generate_pass()
    user = User()
    user.username = slug
    user.set_password(password)
    count = 0
    save_user(user, slug, count)
    user.groups.add(member_group)
    person.user = user
    person.save()
