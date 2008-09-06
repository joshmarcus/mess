from django.db import models
from django.contrib.auth.models import User

addressTYPES = (
    ('h','Home'),
    ('w','Work'),
    ('o','Other'),
)
PHONE_TYPES = (
    ('h','Home'),
    ('w','Work'),
    ('m','Mobile'),
    ('o','Other'),
)
EMAIL_TYPES = (
    ('p','Personal'),
    ('w','Work'),
    ('s','School'),
    ('o','Other'),
)
 
class Address(models.Model):
    type = models.CharField(max_length=1, choices=addressTYPES, default='h')
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, default='Philadelphia')
    # state is CharField to allow for international
    state = models.CharField(max_length=50, default='PA')
    # postal_code is CharField for the same reason as state
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='USA')
    
    def __unicode__(self):
        if self.address2:
            return ('%s, %s' % (self.address1, self.address2))
        else:
            return self.address1

    class Meta:
        verbose_name_plural = 'Addresses'

class Phone(models.Model):
    type = models.CharField(max_length=1, choices=PHONE_TYPES, default='h')
    # PhoneNumberField is not international-compliant
    number = models.CharField(max_length=20)
    ext = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        # Why doesn't get_type_display work here:
        #phone = ('%s: %s' % (self.get_type_display, self.number))
        if self.ext:
            return '%s Ext %s' % (self.number, self.ext)
        else:
            return self.number

class Email(models.Model):
    type = models.CharField(max_length=1, choices=EMAIL_TYPES, default='p')
    email = models.EmailField()

    def __unicode__(self):
        return self.email

# possibly include IM and URL classes at some point

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    addresses = models.ManyToManyField(Address, blank=True, null=True)
    phones = models.ManyToManyField(Phone, blank=True, null=True)
    emails = models.ManyToManyField(Email, blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ['user']

