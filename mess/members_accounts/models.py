from django.db import models

from mess.contacts.models import Email, Phone, Address
from mess.work.models import Job

class Account(models.Model):
    name = models.CharField(maxlength=40)
    contact = models.ForeignKey('Member', related_name='Member.account')

    def __str__(self):
        return '%s' % (self.name)
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass

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
        ('L', 'Leave of Absence'),
        ('q', 'Quit'),
        ('m', 'Missing'),  # Member has disappeared without notice.
        ('i', 'Inactive'),
    )

    CONTACT_PREF = (
        ('e', 'Email'),
        ('t', 'Telephone'),
    )

    user = models.CharField(maxlength=20, blank=True, unique=True)
    password = models.CharField(maxlength=96, blank=True)
    role = models.CharField(maxlength=1, choices=ROLE_CHOICES,
                            default=STATUS_CHOICES[0], radio_admin=True)
    given = models.CharField(maxlength=20, blank=True)
    middle = models.CharField(maxlength=20, blank=True)
    family = models.CharField(maxlength=20, blank=True)
    status = models.CharField(maxlength=1, choices=STATUS_CHOICES,
                            default='a', radio_admin=True)
    date_joined = models.DateField()
    has_key = models.BooleanField(default=False)
    job = models.ForeignKey(Job)
    
    accounts = models.ManyToManyField(Account, blank=True)
    account = models.ForeignKey(Account, verbose_name='Primary Account',
                                related_name='accounts', blank=True)
    
    emails = models.ManyToManyField(Email, blank=True)
    phones = models.ManyToManyField(Phone, blank=True)
    address = models.ForeignKey(Address, blank=True)

    # All the members preference stuff.  I put it in here to replicate
    # the MySQL schema. I'm not sure what will work best in Django

    contact_by = models.CharField(maxlength=1, choices=CONTACT_PREF,
                                default='e', radio_admin=True)
    email = models.ForeignKey(Email, verbose_name='Prefered Email Address',
                                related_name='emails', blank=True)
    phone = models.ForeignKey(Phone, verbose_name='Prefered Phone Number',
                                related_name='phones', blank=True)

    def __str__(self):
        return '%s %s %s' % (self.given, self.middle, self.family)
    
    class Meta:
        ordering = ['given']

    class Admin:
        fields = (
            (None, {
                'fields': (('given', 'middle', 'family'),
                            ('user', 'password'), 'date_joined', 'status',
                            'role', ('has_key', 'job'))
                }),
            ('Accounts', {
                'classes': 'collapse',
                'fields' : (('account', 'accounts'),),
                }),
            ('Contact', {
                'classes': 'collapse',
                'fields' : (('email', 'emails'), ('phone', 'phones'),
                            'address'),
                }),
        )

