from django.shortcuts import render, redirect
from uploader.forms import UploadedFileForm
from uploader.models import UploadedFile, Project
from django.urls import reverse
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('/projects')
    return render(request, 'login.html')

def projects(request):
    if request.method == 'POST':
        return redirect('/'+request.POST['project'])
    groups = request.user.groups.all()
    projects = Project.objects.filter(group__in=groups)
    return render(request, 'projects.html', {
        'projects': projects
    })
# Create your views here.
def uploader(request, project=None):
    form = UploadedFileForm()
    files = UploadedFile.objects.filter(user=request.user, project=project)
    revisions = [f.revision for f in files]
    revisions = list(set(revisions))

    if request.method == 'POST':
        #TODO: request.FILES?
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('uploader'))

    return render(request, 'dashboard.html', {
        'form': form,
        'files': files,
        'revisions': revisions,
    })

def revisions(request):
    files = UploadedFile.objects.all()
    revisions = [f.revision for f in files]
    revisions = list(set(revisions))
    form = UploadedFileForm()
    files = UploadedFile.objects.filter(revision=request.POST['revision'])

    return render(request, 'dashboard.html', {
        'form': form,
        'files': files,
        'revisions': revisions,
    })
