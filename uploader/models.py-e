import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User,Group

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<username>/<filename>
    return '{0}/{1}/{2}'.format(instance.user.username, instance.project, filename)

class Project(models.Model):
    name = models.CharField(max_length=20)
    group = models.ForeignKey(Group)

    def __str__(self):
        return self.name

# Create your models here.
class UploadedFile(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    name = models.CharField(max_length=20, blank=True) #TODO:need both blank and null?
    revision = models.IntegerField() #TODO: ???
    project = models.ForeignKey(Project)
    note = models.CharField(max_length=256, blank=True)
    datetime = models.DateTimeField()
    user = models.ForeignKey(User)

    def readable_file_name(self):
        return str(self.file).split('/')[2]

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension
