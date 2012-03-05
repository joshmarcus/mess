from django.db import models

from datetime import datetime

import mess.membership.models as m_models

class Location(models.Model):
    name = models.CharField(unique=True, max_length=50)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, default='Philadelphia')
    state = models.CharField(max_length=50, default='PA')
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='USA')
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class Event (models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(null=True, max_length=255)
    datetime = models.DateTimeField(default=datetime.now())
    length_in_minutes = models.IntegerField(default=120)
    location = models.ForeignKey(Location, limit_choices_to={'active': True}, null=True)
    staff_contact = models.ForeignKey('membership.Member', related_name='staff_contacts', null=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class Orientation(Event):
    facilitator = models.ForeignKey('membership.Member', related_name='facilitators', null=True)
    cofacilitator = models.ForeignKey('membership.Member', related_name='cofacilitators', null=True)
