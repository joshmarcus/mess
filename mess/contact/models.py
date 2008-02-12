from django.db import models

ADDRESS_TYPES = (
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
    type = models.CharField(max_length=1, choices=ADDRESS_TYPES)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, default='Philadelphia')
    # state is CharField to allow for international
    state = models.CharField(max_length=50, default='PA')
    # postal_code is CharField for the same reason as state
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='USA')
    
    def __unicode__(self):
        return self.address1

    class Admin:
        pass

    class Meta:
        verbose_name_plural = 'Addresses'

class Phone(models.Model):
    type = models.CharField(max_length=1, choices=PHONE_TYPES)
    # PhoneNumberField is not international-compliant
    number = models.PhoneNumberField()
    ext = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.number

    class Admin:
        pass

class Email(models.Model):
    type = models.CharField(max_length=1, choices=EMAIL_TYPES)
    email = models.EmailField()

    def __unicode__(self):
        return self.email

    class Admin:
        pass

# possibly include IM and URL classes at some point
