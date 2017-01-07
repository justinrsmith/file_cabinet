from __future__ import unicode_literals

from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=20)

# Create your models here.
class UploadedFile(models.Model):
    file = models.FileField()
    name = models.CharField(max_length=20, blank=True) #TODO:need both blank and null?
    revision = models.IntegerField() #TODO: ???
    project = models.ForeignKey(Project)
