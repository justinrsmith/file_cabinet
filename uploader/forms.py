from django import forms
from uploader.models import UploadedFile, Project
from django.contrib.auth.models import User

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

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
        }
    ))

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


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})

    def clean(self):
        data_keys = self.cleaned_data.keys()
        if not 'first_name' in data_keys:
            raise forms.ValidationError('All fields are required.')
        elif not 'last_name' in data_keys:
            raise forms.ValidationError('All fields are required.')
        elif not 'email' in data_keys:
            raise forms.ValidationError('All fields are required.')

    def clean_first_name(self):
        if not self.cleaned_data.get('first_name'):
            raise forms.ValidationError('First name cannot be blank.')

    def clean_last_name(self):
        if not self.cleaned_data.get('last_name'):
            raise forms.ValidationError('Last name cannot be blank.')

    def clean_email(self):
        if not self.cleaned_data.get('email'):
            raise forms.ValidationError('Email cannot be blank.')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['description'].widget.attrs.update({'class' : 'form-control'})

    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
