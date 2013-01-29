from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    user = models.OneToOneField(User)
    token = models.CharField(max_length=255)


class Clients(models.Model):
    login = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    agent = models.ForeignKey(User)
    yml = models.URLField(blank=True)
    ymltype = models.CharField(max_length=3, choices=(('xml','xml'),('xl','xl')), default='xml')
    
    
    def __unicode__(self):
        return self.name