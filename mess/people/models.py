from django.db import models
from django.contrib.auth.models import User

from mess.contact.models import Address, Phone, Email

class Person(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    addresses = models.ManyToManyField(Address)
    phones = models.ManyToManyField(Phone)
    emails = models.ManyToManyField(Email)

    def __unicode__(self):
        return self.name

    class Admin:
        pass
