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
]

class UploadedFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadedFileForm, self).__init__(*args, **kwargs)
        self.fields['revision'].widget.attrs.update({'class' : 'form-control'})
        self.fields['name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['note'].widget.attrs.update({'class' : 'form-control'})

    def clean(self):
        if not self.cleaned_data.get('revision', None):
            raise forms.ValidationError('Please fill out all of the required fields below.')
        elif not self.cleaned_data.get('file', None):
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
        return file

    class Meta:
        model = UploadedFile
        fields = ['revision', 'name', 'file', 'note']
        label = {
            'file': 'Select File'
        }
