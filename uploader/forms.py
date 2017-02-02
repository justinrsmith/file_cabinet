from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from uploader.models import UploadedFile, Project

ALLOWED_EXTENSIONS = [
    'jpg',
    'jpeg',
    'png',
    'zip',
    'psd',
    'xlsx',
    'csv',
    'py',
    'txt',
]

MAX_UPLOAD_SIZE = 52428800

class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].label = 'Email'
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if username:
            return username.lower()

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', None)
        if not first_name:
            raise forms.ValidationError('This field is required.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', None)
        if not last_name:
            raise forms.ValidationError('This field is required.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if not email:
            raise forms.ValidationError('This field is required.')
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password', None)
        password_confirm = self.cleaned_data.get('password_confirm', None)
        if not password_confirm:
            raise forms.ValidationError('This field is required.')
        elif not password == password_confirm:
            raise forms.ValidationError('Password must match.')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']


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
        self.fields['display_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['note'].widget.attrs.update({'class' : 'form-control'})
        self.fields['file'].label = 'Select File'

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
        file = self.cleaned_data.get('file', None)
        if file:
            name, ext = file.name.split('.')
            uploaded_files = UploadedFile.objects.filter(file__contains=name, revision=revision)
            if uploaded_files:
                raise forms.ValidationError('%s already exists in project for revision number %s.' % (file.name, revision))
        return revision

    def clean_file(self):
        file = self.cleaned_data.get('file')
        name, ext = file.name.split('.')
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError('%s is not an allowed file type.' % ext)
        elif file.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('%s is greater than 50mb.' % ext)
        return file

    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name', None)
        if display_name:
            revision = self.cleaned_data.get('revision')
            if '.' in display_name:
                name, ext = display_name.split('.')
            #TODO: pep8/django style check
            uploaded_files = UploadedFile.objects.filter(
                Q(file__contains=display_name) | Q(display_name=display_name),
                revision=revision
            )
            if uploaded_files:
                raise forms.ValidationError(
                    '%s already exists in project for revision number %s.' % (display_name, revision))
        return self.cleaned_data.get('display_name')

    class Meta:
        model = UploadedFile
        fields = ['file', 'revision', 'display_name',  'note']
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


class EditProjectForm(forms.ModelForm):

    class Meta:
        model  = Project
        fields = '__all__'
