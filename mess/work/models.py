from django.db import models

class Job(models.Model):
    name = models.CharField(maxlength=40)

    def __str__(self):
        return smart_str('%s' % (self.name))

