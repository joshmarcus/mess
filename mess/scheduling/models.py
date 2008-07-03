from django.db import models

class Job(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass

