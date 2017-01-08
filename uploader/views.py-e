from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from uploader.forms import UploadedFileForm
from uploader.models import UploadedFile, Project

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
        return redirect('/filecabinet/'+request.POST['project'])
    groups = request.user.groups.all()
    projects = Project.objects.filter(group__in=groups)
    return render(request, 'projects.html', {
        'projects': projects
    })

@login_required
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
            uploaded_file = form.save(commit=False)
            uploaded_file.project_id = project
            uploaded_file.user_id = request.user.id
            uploaded_file.save()
            return redirect('/filecabinet/'+project)

    return render(request, 'dashboard.html', {
        'form': form,
        'files': files,
        'revisions': revisions,
        'project': project
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
