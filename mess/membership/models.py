from datetime import date

from django.db import models

from mess.work.models import Job


class Address(models.Model):
    address_1 = models.CharField(max_length=40)
    address_2 = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=40, default='Philadelphia')
    state = models.USStateField(default='PA')
    zip_1 = models.PositiveIntegerField(max_length=5, null=True, blank=True)
    zip_2 = models.PositiveIntegerField(max_length=4, null=True, blank=True)
    
    def __str__(self):
        return '%s' % (self.address_1)

    class Admin:
        pass


class Account(models.Model):

    def balance():
        return balance

    name = models.CharField(max_length=40, unique=True)
    contact = models.ForeignKey('Member', related_name='Member.account',
                                blank=True, null=True)
    balance = models.DecimalField(max_digits=4, decimal_places=2,
                                blank=True, null=True)

    def __unicode__(self):
        return '%s' % (self.name)
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass


class Member(models.Model):

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

    LOCATION_CHOICES = (
        ('u','Unknown'),
        ('h','Home'),
        ('w','Work'),
        ('m','Mobile'),
        ('o','Other'),
    )

    TYPE_CHOICES = (
        ('u','Unknown'),
        ('v','Voice'),
        ('m','Voice Mail'),
        ('p','Pager'),
        ('f','Fax'),
    )

    CONTACT_CHOICES = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
    )

    given = models.CharField(max_length=20, blank=True)
    middle = models.CharField(max_length=20, blank=True)
    family = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                            default='a', radio_admin=True)
    date_joined = models.DateField(default=date(1900, 01, 01))
    has_key = models.BooleanField(default=False)
    job = models.ForeignKey(Job)
    
    accounts = models.ManyToManyField(Account, blank=True, null=True)
    account = models.ForeignKey(Account, verbose_name='Primary Account',
                                related_name='accounts',blank=True, null=True)
    
    address = models.ForeignKey(Address, blank=True, null=True)
    contact_by = models.CharField(max_length=1, choices=CONTACT_PREF,
                                default='e', radio_admin=True)
    prefered_phone = models.CharField(max_length=1, choices=CONTACT_CHOICES,
                                        default='1',)
    prefered_email = models.CharField(max_length=1, choices=CONTACT_CHOICES,
                                        default='1',)

    phone_1 = models.PhoneNumberField(verbose_name='Phone 1', 
                                    null=True, blank=True)
    phone_1_ext = models.PositiveIntegerField(max_length=5,
                                            verbose_name='Phone 1 Ext',
                                            null=True, blank=True,)
    phone_1_loc = models.CharField(max_length=1,
                                    verbose_name='Phone 1 Location',
                                    default='u', choices=LOCATION_CHOICES)
    phone_1_type = models.CharField(max_length=1, verbose_name='Phone 1 Type',
                                    default='u',choices=TYPE_CHOICES,)
    phone_1_pub = models.BooleanField(default=0, verbose_name='Phone 1 Publish')
    phone_2 = models.PhoneNumberField(verbose_name='Phone 2', 
                                    null=True, blank=True)
    phone_2_ext = models.PositiveIntegerField(max_length=5,
                                            verbose_name='Phone 2 Ext',
                                            null=True, blank=True,)
    phone_2_loc = models.CharField(max_length=1,
                                    verbose_name='Phone 2 Location',
                                    default='u', choices=LOCATION_CHOICES)
    phone_2_type = models.CharField(max_length=1, verbose_name='Phone 2 Type',
                                    default='u',choices=TYPE_CHOICES,)
    phone_2_pub = models.BooleanField(default=0, verbose_name='Phone 2 Publish')

    phone_3 = models.PhoneNumberField(verbose_name='Phone 3', 
                                    null=True, blank=True)
    phone_3_ext = models.PositiveIntegerField(max_length=5,
                                            verbose_name='Phone 3 Ext',
                                            null=True, blank=True,)
    phone_3_loc = models.CharField(max_length=1,
                                    verbose_name='Phone 3 Location',
                                    default='u', choices=LOCATION_CHOICES)
    phone_3_type = models.CharField(max_length=1, verbose_name='Phone 3 Type',
                                    default='u',choices=TYPE_CHOICES,)
    phone_3_pub = models.BooleanField(default=0, verbose_name='Phone 3 Publish')

    email_1 = models.EmailField(null=True, blank=True,)
    email_1_loc = models.CharField(max_length=1,
                                    verbose_name='Email 1 Location',
                                    default='u', choices=LOCATION_CHOICES)
    email_1_pub = models.BooleanField(default=0, verbose_name='Email 1 Publish')
    email_2 = models.EmailField(null=True, blank=True,)
    email_2_loc = models.CharField(max_length=1,
                                    verbose_name='Email 2 Location',
                                    default='u', choices=LOCATION_CHOICES)
    email_2_pub = models.BooleanField(default=0, verbose_name='Email 2 Publish')
    email_3 = models.EmailField(null=True, blank=True,)
    email_3_loc = models.CharField(max_length=1,
                                    verbose_name='Email 3 Location',
                                    default='u', choices=LOCATION_CHOICES)
    email_3_pub = models.BooleanField(default=0, verbose_name='Email 3 Publish')

    def __unicode__(self):
        return '%s %s %s' % (self.given, self.middle, self.family)
    
    class Meta:
        ordering = ['given']

    class Admin:
        pass
    '''
        list_display = ('__str__', 'account',)
        fields = (
            (None, {
                'fields': (('given', 'middle', 'family'),
                            ('user', 'password'), 'date_joined', 'status',
                            'role', ('has_key', 'job', 'address')),
                }),
            ('Accounts', {
                'classes': 'collapse',
                'fields' : (('account', 'accounts'),),
                }),
            ('Contact', {
                'classes': 'collapse',
                'fields' : (('contact_by', 'prefered_email', 'prefered_phone'),
                            ('email_1', 'email_1_loc', 'email_1_pub'),
                            ('email_2', 'email_2_loc', 'email_2_pub'),
                            ('email_3', 'email_3_loc', 'email_3_pub'),
                            ('phone_1', 'phone_1_ext', 'phone_1_type',
                                'phone_1_loc','phone_1_pub'),
                            ('phone_2', 'phone_2_ext', 'phone_2_type',
                                'phone_2_loc', 'phone_2_pub'),
                            ('phone_3', 'phone_3_ext', 'phone_3_type',
                                'phone_3_loc',  'phone_3_pub'),
                            ),
                }),
        )
    '''
