from django.forms import ModelForm
from uploader.models import UploadedFile

class UploadedFileForm(ModelForm):
    class Meta:
        model = UploadedFile
        fields = '__all__'
