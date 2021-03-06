import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<username>/<project>/<revision/<filename>
    return '{0}/{1}/{2}/{3}'.format(instance.user.username, instance.project, instance.revision, filename)


class Project(models.Model):
    name        = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=100, blank=True)
    users       = models.ManyToManyField(User, blank=True, related_name='users')
    #TODO lazy programming fix
    created_by  = models.ForeignKey(User, related_name='created_by', null=True)

    def __str__(self):
        return self.name


# Create your models here.
class UploadedFile(models.Model):
    file         = models.FileField(upload_to=user_directory_path)
    display_name = models.CharField(max_length=20, blank=True) #TODO:need both blank and null?
    revision     = models.IntegerField() #TODO: ???
    project      = models.ForeignKey(Project)
    note         = models.CharField(max_length=256, blank=True)
    datetime     = models.DateTimeField()
    user         = models.ForeignKey(User)

    def readable_file_name(self):
        if self.display_name:
            return self.display_name
        return str(self.file).split('/')[3]

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __str__(self):
        return self.readable_file_name()


class UserActivity(models.Model):
    user = models.OneToOneField(User)#TODO??, on_delete = models.CASCADE)
    last_project = models.ForeignKey(Project)

    def __str__(self):
        return '%s - %s' % (self.user, self.last_project)


@receiver(post_delete, sender=UploadedFile)
def uploadedfile_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
