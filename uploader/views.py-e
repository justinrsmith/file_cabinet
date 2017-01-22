import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from uploader.models import UploadedFile, Project, UserActivity
from uploader.forms import UploadedFileForm, EditProfileForm, LoginForm, ProjectForm, RegistrationForm

def register_user(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('password_confirm')
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            messages.success(
                request, 'Thank you, %s you have been successfully registered.' % new_user.username
                )
            return redirect('/')
    return render(request, 'registration.html', {
        'form': form
    })

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/uploader')
                else:
                    messages.error(
                        request, ('No active user found for: %s.') % username
                    )
            else:
                messages.error( request, 'Invalid username or password.')
    if request.user.is_authenticated():
        return redirect('/uploader/')
    return render(request, 'login.html', {
        'form': form
    })

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def uploader(request, project=None, revision=None, search=None):
    form = UploadedFileForm()
    projects = Project.objects.filter(users=request.user)
    # If only one project and project wasn't passed in redirect with the one
    # project user has access too
    if len(projects) == 1 and project is None:
        return redirect('/uploader/'+str(projects.first().id))
    if request.method == 'POST':
        #TODO: request.FILES?
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.project_id = project
            uploaded_file.user_id = request.user.id
            uploaded_file.datetime = datetime.now()
            uploaded_file.save()
            file_name = uploaded_file.display_name if uploaded_file.display_name else uploaded_file.file
            messages.success(
                request, '%s has been successfully uploaded.' % uploaded_file.readable_file_name()
                )
            return redirect('/uploader/'+project)
    if project:
        project = Project.objects.get(pk=project)
        obj, created = UserActivity.objects.update_or_create(
            user=request.user,
            defaults={'last_project': project}
        )
        project_files = UploadedFile.objects.filter(
            project_id=project
        ).order_by('-datetime')
        revisions = sorted(list(set([f.revision for f in project_files])))
        if revision:
            project_files = project_files.filter(
                revision=revision
            ).order_by('-datetime')
            revision = int(revision)
        if search:
            project_files = project_files.filter(
                Q(file__contains=search) | Q(display_name__contains=search)
            )
        paginator = Paginator(project_files, 10)
        page = request.GET.get('page', None)
        try:
            project_files = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            project_files = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            project_files = paginator.page(paginator.num_pages)
        return render(request, 'uploader.html', {
            'project': project,
            'projects': projects,
            'form': form,
            'project_files': project_files,
            'revisions': revisions,
            'revision': revision,
            'search_term': search
        })
    user_activity = UserActivity.objects.get(user=request.user)
    if user_activity:
        project = str(user_activity.last_project.id)
        return redirect('/uploader/'+project)

    return render(request, 'uploader.html', {
        'selected_project': project,
        'projects': projects
    })

def get_project(request):
    project = request.POST['project']
    return redirect('/uploader/'+project)

def get_revision(request, project, search=None):
    revision = request.POST['revision']
    if not revision and search:
        return redirect('/uploader/'+project+'/'+search)
    if search:
        return redirect('/uploader/'+project+'/'+revision+'/'+search)
    return redirect('/uploader/'+project+'/'+revision)

def get_search(request, project, revision=None):
    search = request.POST['file_search']
    if revision:
        return redirect('/uploader/'+project+'/'+revision+'/'+search)
    return redirect('/uploader/'+project+'/'+search)

def edit_profile(request, project=None):
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            messages.info(request, 'User profile has been updated.')
            if project:
                return redirect('/uploader/'+project)
            return redirect('/uploader/')
        return render(request, 'edit_profile.html', {
            'user': request.user,
            'form': form,
            'project': project
        })
    data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email
    }
    form = EditProfileForm(initial=data)

    return render(request, 'edit_profile.html', {
        'user': request.user,
        'form': form,
        'project': project
    })

def delete_file(request, project, file):
    UploadedFile.objects.get(pk=file).delete()
    return redirect('/uploader/'+project+'/')

def add_project(request):
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.save()
            new_project.users.add(request.user)

            return redirect('/uploader/'+str(new_project.id))

    return render(request, 'add_project.html', {
        'form': form
    })

def get_file(request, id):
    file = UploadedFile.objects.get(pk=id)
    path = file.file.name
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404
