from django.db import models

from mess.contacts.models import Email, Phone, Address
from mess.work.models import Job

class Account(models.Model):
    name = models.CharField(maxlength=40)
    contact = models.ForeignKey('Member', related_name='Member.account')

    def __str__(self):
        return smart_str('%s' % (self.name))

class Member(models.Model):

    ROLE_CHOICES = (
        ('g', 'Guest'),
        ('m', 'Member'),
        ('c', 'Cashier'),
        ('s', 'Staff'),
    )
    
    STATUS_CHOICES = (
        ('a', 'Active'),
        ('w', 'Working'),  # Member is active and has a job.
        ('n', 'Non-Working'),  # Such as a single parent.
        ('l', 'Leave of Absense'),
        ('q', 'Quit'),
        ('m', 'Missing'),  # Member has disappeared without notice.
        ('i', 'Inactive'),
    )

    CONTACT_PREF = (
        ('e', 'Email'),
        ('t', 'Telephone'),
    )

    user = models.CharField(maxlength=20, unique=True)
    password = models.CharField(maxlength=96)
    role = models.CharField(maxlength=1, choices=ROLE_CHOICES, default='m')
    given = models.CharField(maxlength=20, blank=True)
    middle = models.CharField(maxlength=20, blank=True)
    family = models.CharField(maxlength=20, blank=True)
    status = models.CharField(maxlength=1, choices=STATUS_CHOICES, default='a')
    date_joined = models.DateField()
    has_key = models.BooleanField(default=False)
    job = models.ForeignKey(Job)
    
    accounts = models.ManyToManyField(Account)
    account = models.ForeignKey(Account, verbose_name='Primary Account',
                                related_name='accounts')
    
    emails = models.ManyToManyField(Email, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    address = models.ForeignKey(Address, blank=True)

    # All the members preference stuff.  I put it in here to replicate
    # the MySQL schema. I'm not sure what will work best in Django

    contact_by = models.CharField(maxlength=1, choices=CONTACT_PREF,
                                default='e')
    email = models.ForeignKey(Email, verbose_name='Prefered Email Address',
                                related_name='emails')
    phone = models.ForeignKey(Phone, verbose_name='Prefered Phone Number',
                                related_name='phones')

    def __str__(self):
        return smart_str('%s %s %s' % (self.given, self.middle, self.family))
    

