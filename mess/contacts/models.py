from django.db import models

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
    city = models.CharField(maxlength=40)
    state = models.USStateField()
    zip_1 = models.PositiveIntegerField(maxlength=5, null=True, blank=True)
    zip_2 = models.PositiveIntegerField(maxlength=4, null=True, blank=True)
    
    def __str__(self):
        return '%s' % (self.address_1)

    class Admin:
        pass

