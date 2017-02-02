import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from uploader.models import UploadedFile, Project, UserActivity
from uploader.forms import UploadedFileForm, EditProfileForm, LoginForm, ProjectForm, RegistrationForm, EditProjectForm

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
            username = request.POST['username'].lower()
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

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def uploader(request, project=None, revision=None, search=None):
    form = UploadedFileForm()
    projects = Project.objects.filter(users=request.user)
    try:
        project = Project.objects.get(pk=project)
    except Project.DoesNotExist:
        pass #TODO: best way to do this?
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.project = project
            uploaded_file.user_id = request.user.id
            uploaded_file.datetime = datetime.now()
            uploaded_file.save()
            project_users = [user.email for user in project.users.all()]
            # Build and send email message to all users on project besides
            # the user who uploaded
            subject = 'A new file has been uploaded to %s' % project.name
            body = """
                A new file called %s has been uploaded into file
                cabinet by %s for the project %s.
            """ % (uploaded_file.readable_file_name(), request.user.username, project.name)
            message = EmailMessage(
                subject,
                body,
                bcc=project_users #bcc
            )
            #message.send()
            messages.success(
                request, '%s has been successfully uploaded.' % uploaded_file.readable_file_name()
                )
            return redirect('/uploader/'+str(project.id))
    if project:
        obj, created = UserActivity.objects.update_or_create(
            user=request.user,
            defaults={'last_project': project}
        )
        project_files = UploadedFile.objects.filter(
            project=project
        ).order_by('-datetime')
        recently_uploaded = project_files[:14]
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
            'search_term': search,
            'recently_uploaded': recently_uploaded
        })
    try:
        user_activity = UserActivity.objects.get(user=request.user)
        project = str(user_activity.last_project.id)
        return redirect('/uploader/'+project)
    except UserActivity.DoesNotExist:
        return render(request, 'uploader.html', {
            'selected_project': project,
            'projects': projects
        })

@login_required
def get_revision(request, project, search=None):
    revision = request.POST['revision']
    if not revision and search:
        return redirect('/uploader/'+project+'/'+search)
    if search:
        return redirect('/uploader/'+project+'/'+revision+'/'+search)
    return redirect('/uploader/'+project+'/'+revision)

@login_required
def get_search(request, project, revision=None):
    search = request.POST['file_search']
    if revision:
        return redirect('/uploader/'+project+'/'+revision+'/'+search)
    return redirect('/uploader/'+project+'/'+search)

@login_required
#TODO: rewrite this please :(
def edit_profile(request, project=None):
    if request.method == 'POST':
        if project:
            project = Project.objects.get(pk=project)
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            messages.info(request, 'User profile has been updated.')
            if project:
                return redirect('/uploader/'+str(project.id))
            return redirect('/uploader/')
        return render(request, 'edit_profile.html', {
            'user': request.user,
            'form': form,
            'project': project
        })
    else:
        form = EditProfileForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        })
        if project:
            project = Project.objects.get(pk=project)
            return render(request, 'edit_profile.html', {
                'user': request.user,
                'form': form,
                'project': project
            })
        return render(request, 'edit_profile.html', {
            'user': request.user,
            'form': form
        })

@login_required
def delete_file(request, project, file):
    UploadedFile.objects.get(pk=file).delete()
    return redirect('/uploader/'+project+'/')

@login_required
def get_or_create_project(request, project=None):
    form = ProjectForm()
    projects = Project.objects.filter(users=request.user)
    #TODO: is this legit?
    try:
        curr_proj = Project.objects.get(pk=project)
        form = ProjectForm(instance=curr_proj)
    except Project.DoesNotExist:
        pass
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect('/uploader/'+str(project.id))
    return render(request, 'add_project.html', {
        'form': form,
        'projects': projects,
        'project': project
    })

@login_required
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
