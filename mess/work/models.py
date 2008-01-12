from django.db import models

class Job(models.Model):
    name = models.CharField(maxlength=40, unique=True)

    def __str__(self):
        return '%s' % (self.name)
    
    class Meta:
        ordering = ['name']

    class Admin:
        pass

