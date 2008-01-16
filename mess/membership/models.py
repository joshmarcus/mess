from datetime import date

from django.db import models

from mess.work.models import Job


class Email(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return '%s' % (self.email)

    class Admin:
        pass


class Phone(models.Model):
    number = models.PhoneNumberField(unique=True)
    extension = models.PositiveIntegerField(maxlength=5, null=True, blank=True)

    def __str__(self):
        if self.extension:
            return '%s ext: %s' % (self.number, self.extension)
        else:
            return '%s' % (self.number)

    class Admin:
        pass


class Address(models.Model):
    address_1 = models.CharField(maxlength=40)
    address_2 = models.CharField(maxlength=40, blank=True)
    city = models.CharField(maxlength=40, default='Philadelphia')
    state = models.USStateField(default='PA')
    zip_1 = models.PositiveIntegerField(maxlength=5, null=True, blank=True)
    zip_2 = models.PositiveIntegerField(maxlength=4, null=True, blank=True)
    
    def __str__(self):
        return '%s' % (self.address_1)

    class Admin:
        pass

'''
class Attribute(models.Model):

    LOCATION_CHOICES = (
        ('u','Unknown'),
        ('h','Home'),
        ('w','Work'),
        ('m','Mobile'),
        ('o','Other'),
    )

    public = models.BooleanField()
    location = models.CharField(maxlength=1, default='u')


class EmailAttribute(Attribute):
    email = models.ForeignKey(Email)
    member = models.ForeignKey('Member')


class PhoneAttribute(Attribute):
    
    TYPE_CHOICES = (
        ('u','Unknown'),
        ('v','Voice'),
        ('m','Voice Mail'),
        ('p','Pager'),
        ('f','Fax'),
    )

    phone = models.ForeignKey()
    member = models.ForeignKey('Member')
    type = models.CharField(maxlength=1, default='u')


class AddressAttribute(Attribute):
    email = models.ForeignKey(Email)
    member = models.ForeignKey('Member')
'''

class Account(models.Model):

    def balance():
        return b

    name = models.CharField(maxlength=40, unique=True)
    contact = models.ForeignKey('Member', related_name='Member.account',
                                blank=True, null=True)
    #balance = models.DecimalField(max_digit=4, decimal_places=2,
    #                            blank=True, null=True)
    balance = models.IntegerField(default=0, blank=True, null=True)

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
                            default='m', radio_admin=True)
    given = models.CharField(maxlength=20, blank=True)
    middle = models.CharField(maxlength=20, blank=True)
    family = models.CharField(maxlength=20, blank=True)
    status = models.CharField(maxlength=1, choices=STATUS_CHOICES,
                            default='a', radio_admin=True)
    date_joined = models.DateField(default=date(1900, 01, 01))
    has_key = models.BooleanField(default=False)
    job = models.ForeignKey(Job)
    accounts = models.ManyToManyField(Account, blank=True, null=True)
    account = models.ForeignKey(Account, verbose_name='Primary Account',
                                related_name='accounts',blank=True, null=True)
    address = models.ForeignKey(Address, blank=True, null=True)
    contact_by = models.CharField(maxlength=1, choices=CONTACT_PREF,
                                default='e', radio_admin=True)
    emails = models.ManyToManyField(Email, blank=True, null=True)    
    email = models.ForeignKey(Email, verbose_name='Prefered Email Address',
                                related_name='emails', blank=True, null=True)
    phones = models.ManyToManyField(Phone, blank=True, null=True)    
    phone = models.ForeignKey(Phone, verbose_name='Prefered Phone Number',
                                related_name='phones', blank=True, null=True)

    def __str__(self):
        return '%s %s %s' % (self.given, self.middle, self.family)
    
    class Meta:
        ordering = ['given']

    class Admin:
        list_display = ('__str__', 'account')
        fields = (
            (None, {
                'fields': (('given', 'middle', 'family'),
                            ('user', 'password'), 'date_joined', 'status',
                            'role', 'status', ('has_key', 'job')),
                }),
            ('Accounts', {
                'classes': 'collapse',
                'fields' : (('account', 'accounts'),),
                }),
            ('Contact', {
                'classes': 'collapse',
                'fields' : ('contact_by', ('email', 'emails'),
                            ('phone', 'phones'),
                            'address'),
                }),
        )
