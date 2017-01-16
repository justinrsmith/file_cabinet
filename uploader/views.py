from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from uploader.models import UploadedFile, Project
from uploader.forms import UploadedFileForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('/uploader')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def uploader(request, project=None, revision=None):
    form = UploadedFileForm()
    if request.method == 'POST':
        #TODO: request.FILES?
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.project_id = project
            uploaded_file.user_id = request.user.id
            uploaded_file.datetime = datetime.now()
            uploaded_file.save()
            file_name = uploaded_file.name if uploaded_file.name else uploaded_file.file
            messages.success(
                request, '%s has been successfully uploaded.' % uploaded_file.readable_file_name()
                )
            return redirect('/uploader/'+project)

    user_groups = request.user.groups.all()
    projects = Project.objects.filter(group__in=user_groups)
    if project:
        project = Project.objects.get(pk=project)
        project_files = UploadedFile.objects.filter(
            user=request.user,
            project_id=project
        ).order_by('-datetime')
        revisions = list(set([f.revision for f in project_files]))
        if revision:
            project_files = project_files.filter(
                revision=revision
            ).order_by('-datetime')
            revision = int(revision)
        return render(request, 'uploader.html', {
            'project': project,
            'projects': projects,
            'form': form,
            'project_files': project_files,
            'revisions': revisions,
            'revision': revision
        })

    return render(request, 'uploader.html', {
        'selected_project': project,
        'projects': projects
    })test

def get_project(request):
    project = request.POST['project']
    return redirect('/uploader/'+project)

def get_revision(request, project):
    revision = request.POST['revision']
    return redirect('/uploader/'+project+'/'+revision)

def delete_file(request, project, file):
    UploadedFile.objects.get(pk=file).delete()
    return redirect('/uploader/'+project+'/')
