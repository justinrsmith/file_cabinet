from django import forms
from uploader.models import UploadedFile

ALLOWED_EXTENSIONS = [
    'jpg',
    'jpeg',
    'png',
    'zip',
    'psd',
    'xlsx',
    'csv',
    'py',
]

MAX_UPLOAD_SIZE = 5242880

class UploadedFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadedFileForm, self).__init__(*args, **kwargs)
        self.fields['revision'] .widget.attrs.update({
            'class': 'form-control',
            'style': 'width:25%;',
            'min': '0'
        })
        self.fields['name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['note'].widget.attrs.update({'class' : 'form-control'})

    def clean(self):
        data = self.cleaned_data
        # If user provides a file but a poor revision number
        if not data.get('revision', None) and data.get('file', None):
            raise forms.ValidationError('Please fix the errors below.')
        # If user provides a revision but a file that errors
        elif data.get('revision', None) and not data.get('file', None):
            raise forms.ValidationError('Please fix the errors below.')
        elif not data.get('revision', None):
            raise forms.ValidationError('Please fill out all of the required fields below.')
        elif not data.get('file', None):
            raise forms.ValidationError('Please fill out all of the required fields below.')

    def clean_revision(self):
        revision = self.cleaned_data.get('revision')
        if revision < 1:
            raise forms.ValidationError('Revision must be a number greater than zero.')
        return revision

    def clean_file(self):
        file = self.cleaned_data.get('file')
        name, ext = file.name.split('.')
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError('%s is not an allowed file type.' % ext)
        elif file.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('%s is greater than 50mb.' % ext)
        return file

    class Meta:
        model = UploadedFile
        fields = ['file', 'revision', 'name',  'note']
        label = {
            'file': 'Select File'
        }
