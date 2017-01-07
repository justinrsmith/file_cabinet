import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User,Group

class Project(models.Model):
    name = models.CharField(max_length=20)
    group = models.ForeignKey(Group)

    def __str__(self):
        return self.name

# Create your models here.
class UploadedFile(models.Model):
    file = models.FileField()
    name = models.CharField(max_length=20, blank=True) #TODO:need both blank and null?
    revision = models.IntegerField() #TODO: ???
    project = models.ForeignKey(Project)
    datetime = models.DateTimeField(default=timezone.now())
    user = models.ForeignKey(User)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension
