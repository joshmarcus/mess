from django.db import models

class Email(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return smart_str('%s' % (self.email))

class Phone(models.Model):
    number = models.PhoneNumberField(unique=True)
    extension = models.PositiveIntegerField(maxlength=5)

    def __str__(self):
        if self.extention:
            return smart_str('%s ext: %s' % (self.number, self.extention))
        else:
            return smart_str('%s' % (self.number))

class Address(models.Model):
    address_1 = models.CharField(maxlength=40)
    address_2 = models.CharField(maxlength=40, blank=True)
    city = models.CharField(maxlength=40)
    state = models.USStateField()
    zip_1 = models.PositiveIntegerField(maxlength=5)
    zip_2 = models.PositiveIntegerField(maxlength=4)
    
    def __str__(self):
        return smart_str('%s' % (self.address_1))
