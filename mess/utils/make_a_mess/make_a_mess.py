import sys, os, random
from datetime import date

MESS_PATH = '/home/digger/src/SVN/mess/trunk/mess'
sys.path.append(MESS_PATH)

from django.core.management import setup_environ
import settings

setup_environ(settings)

from people.models import Person
from membership.models import Member, Account
from membership.models import MEMBER_STATUS, WORK_STATUS
from work.models import Job
from contact.models import Email, Phone, Address
from contact.models import EMAIL_TYPES, PHONE_TYPES, ADDRESS_TYPES

from names import GIVEN_NAMES, FAMILY_NAMES, INITIALS
from contacts import DOMAIN_NAMES, AREA_CODES
from addresses import STREET_NAMES, ADDRESS_2, ADDRESS_2_PRE, ADDRESS_2_POST
from accounts import ACCOUNT_NAMES
from jobs import JOB_NAMES


def create_jobs():
    for n in JOB_NAMES:
        try:
            Job.objects.get(name = n)
            print ('%s is already a job' % n)
        except:
            j = Job(name = n)
            j.save()

def make_a_person(max=1):
    g, m, f = '','',''
    i = 1
    while i <= max:
        i += 1
        rg = random.randint(1,20)    
        if rg >= 3:
            g = random.choice(GIVEN_NAMES)
        elif rg == 2:
            g = random.choice(INITIALS)

        rm = random.randint(1,50)    
        if rm  == 49:
            m = random.choice(GIVEN_NAMES)
        elif rm == 50:
            m = random.choice(INITIALS)

        rf = random.randint(0,10)    
        if rf >= 1:
            f = random.choice(FAMILY_NAMES)
        
        name = ' '.join(('%s %s %s' %  (g, m, f)).split())
        if name == '':
            print('The name is empty!')
            return
        else:
            p = Person(name=name)
            p.save()
            print('Created person named %s' % p.name)
        
def assign_email(id, min=0, max=1):
    """Randomly generate and save an email addrsss to a Person that
    does not yet have one.  Optionally generate and assign addtional
    email addresses using the number parameter.
    """

    try:
        person = Person.objects.get(id=id)
    except:
        print('Sorry no one by that id')
    if min <= person.emails.count() >= max:
        print('%s already has %s email addresses.' %
                (person.name, person.emails.count())
                )
    elif random.randint(1,20) >= 5:
        d = random.choice(DOMAIN_NAMES)
        t = random.choice(EMAIL_TYPES)
        names = person.name.split()
        rand = random.randint(1,100)
        if rand == 1:
            n = names[0]
        elif rand <= 50:
            n = names[0] + '.' + names.pop()
        else:
            n = random.choice(names) + str(random.randint(1,9999))
        e = Email(type=t[0], email=(n + '@' + d))
        e.save()
        person.emails.add(e)
        print('Added %s for %s.' %
                (person.emails.get(id=e.id).email, person.name)
                )
    else:
        print("I pass on email.")

def assign_phone(id, min=0, max=1):
    """Randomly generate and save a phone number to a Person that
    does not yet have one.  Optionally generate and assign addtional
    phone numbers with the min ans max parameters.
    """

    try:
        person = Person.objects.get(id=id)
    except:
        print('Sorry no one by that id')
    if min <= person.phones.count() >= max:
        print('%s has %s phone numbers.' %
                (person.name, person.phones.count())
                )
    elif random.randint(1,20) >= 5:
        t = random.choice(PHONE_TYPES)
        ac = random.choice(AREA_CODES)
        e = random.randint(100,999)
        n = random.randint(1000,9999)
        p = Phone(type=t[0], number=('%s-%s-%s' % (ac, e, n)))
        if random.randint(1,100) == 1 and t == 'w':
            ext = random.randint(1,999)
            p.ext = ext
        p.save()
        person.phones.add(p)
        #print t, ac, e, n
        print('Added %s for %s.' %
                (person.phones.get(id=p.id), person.name)
                )
    else:
        print("I pass on a phone number.")


def generate_address(number=1):
    """Randomly generate an address"""

    if number == 1 and random.randint(1,100) == 1:
        t = random.choice(ADDRESS_TYPES)[0]
    else:
        t = 'h'
    rand = random.randint(0,20)
    if rand == 18:
        a_2 = random.choice(ADDRESS_2)
    if rand == 19:
        a_2 = ('%s%s' %
                (random.choice(ADDRESS_2_PRE), random.randint(1,2000))
                )
    if rand == 19:
        a_2 = ('%s%s' %
                (random.randint(1,2000), random.choice(ADDRESS_2_POST))
                )
    a_1 = ('%s %s' %
            (random.randint(1, 6000), random.choice(STREET_NAMES)))
    if rand != 0:
        z = '19' + str(random.randint(100, 200))
    a = Address(type=t, address_1=a_1)
    try:
        a_2
        a.address_2 = a_2
    except:
        pass
    try:
        z
        a.postal_code = z
    except:
        pass
    return a

def assign_address(id, min=1, max=2):
    """Assign an Address to a Person that does not yet have one.
    Optionally generate and assign addtional addresses with the min
    and max parameters.
    """
    def get_address():
        if random.randint(1,200) >= 1:
            a = generate_address(1)
            a.save()
            person.addresses.add(a)
            person.save()
            print 
            print('Added %s for %s.' %
                    (a, person.name)
                    )

    def test_for_max():
        if person.addresses.count() >= max:
            print('%s has %s addresses.' %
                    (person.name, person.addresses.count())
                    )
            return True
        return False

    # First give an Address to the Account.contacts
    try:
        person = Person.objects.get(id=id)
    except:
        print('Sorry no one by that id')
    try:
        account = Account.objects.get(contact=id)
        if not test_for_max():
            #a = contact..
            get_address()
    except:
        print('Sorry, that id is not an Account.contact')
        if test_for_max():
            pass
        else:
            print("I'll pass on an address.")

def create_accounts():
    """Generate and save a account.  Fill it with members"""
    def can_shop():
        if random.randint(0,10) >= 9:
            return False
        else:
            return True

    def create_from_list():
        # Create the accounts with names in ACCOUNT_NAMES
        for name in ACCOUNT_NAMES:
            try:
                Account.objects.get(name=name)
                print ('%s is already an Account' % name)
            except:
                member = random.choice(Member.objects.all())
                a = Account(name=name, contact=member, can_shop=can_shop())
                a.save()
                a.members.add(member)
                a.save()
                print('Created new account named %s.  Contact is %s ' %
                        (a.name, a.contact))
    
    def fill_accounts():
        #Give the accounts more members
        for account in Account.objects.all():
            print('Filling %s with members' % account.name)
            max = 5
            max_members = random.randint(1, 5)
            i = 0
            while account.members.count() <= max_members :
                i += 1
                if i >= Member.objects.count():
                    print('I\'m tired of trying. Giving up!')
                    break
                else:
                    member = random.choice(Member.objects.all())
                    rand = random.randint(0,50)
                    if member.accounts.count() >= 1 and  rand == 0:
                        try:
                            account.members.get(id=member.id)
                            print('%s is already in account %s' %
                                    (member.name, account.name)
                                    )
                        except:
                            account.members.add(member.id)
                            account.save()
                            print('Added %s to %s' %
                                    (member.person.name, account.name))
    
    def use_member_name():
        # Create more accounts using the Member.person.name
        for member in Member.objects.all():
            member_name = member.person.name 
            if member.accounts.count() != 0:
                print('%s is in %s' %
                        (member_name, member.accounts.latest('id')))
            else:
                print('Creating account for %s' % member_name)
                names = member_name.split()
                rand = random.randint(1,4)
                if rand == 1:
                    account_name = member_name
                if rand == 2:
                    account_name = ('%s\'s House' % names.pop())
                if rand == 3:
                    account_name = ('%s\'s Kitchen' % names[0])
                if rand == 4:
                    account_name = names.pop()
                print('Account name will be %s' % account_name)
                try:
                    
                    Account.objects.get(name=account_name)
                    print('Sorry, %s exists as an account' % account_name)
                except:
                    a = Account(name=account_name, contact=member,
                            can_shop=can_shop())
                    a.save()
                    a.members.add(member)
                    a.save()
                    print('Done creating %s for %s.' % (a.name, member_name))
    
    create_from_list()
    fill_accounts()
    use_member_name()

            
def make_a_member(id):
    """Generate and save a Member using a Person."""

    try:
        person = Person.objects.get(id=id)
    except:
        print('Sorry no one by that id')
    try:
        Member.objects.get(person=person.id)
        print('Sorry, already a member for %s' % person.name)
    except:
        if random.randint(1, 100) != 1:
            if random.randint(0, 500):
                date_joined = date.today()
            else:
                year = random.randint(1977, date.today().year)
                month = random.randint(1,12)            
                day = random.randint(1,28)
                date_joined = date(year, month, day)
            if random.randint(0, 50) >= 5:
                status = 'a'
            else:
                status = random.choice(MEMBER_STATUS)[0]
            if random.randint(0, 50) >= 5:
                work_status = 'w'
            else:
                work_status = random.choice(WORK_STATUS)[0]
            job = random.choice(Job.objects.all())
            m = Member(person=person, date_joined=date_joined,
                        status=status, work_status=work_status, job=job)
            m.save()
            #print t, ac, e, n
            print('Created new member using %s.' % person.name)
        else:
            print("I pass creating a member.")


def make_a_mess(max=100):
    create_jobs()
    while Person.objects.count() <= max:
        make_a_person()
    for person in Person.objects.all():
        make_a_member(person.id)
        assign_email(person.id)
        assign_phone(person.id)
        assign_address(person.id)
    create_accounts()
       
    



