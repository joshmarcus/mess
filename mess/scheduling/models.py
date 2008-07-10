from django.db import models

class ShiftType(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass

class Shift(models.Model):
    type = models.ForeignKey(ShiftType)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    completed = models.BooleanField()

    def __unicode__(self):
        return self.type.name
    
    class Meta:
        ordering = ['start_time']

    class Admin:
        pass

