import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils import timezone

from uploader.models import UploadedFile, Project, UserActivity
from uploader.forms import UploadedFileForm, EditProfileForm, LoginForm,\
                           ProjectForm, RegistrationForm

def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('password_confirm')
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            messages.success(
                request,
                'Thank you, %s you have been successfully registered.' % (
                    new_user.username
                )
            )
            return redirect('/')

    form = RegistrationForm()
    return render(request, 'registration.html', {
        'form': form
    })

def login_view(request):
    if request.user.is_authenticated():
        return redirect('/uploader/')

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

    form = LoginForm()
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
    if project:
        project = Project.objects.get(pk=project)
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES, project=project)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.project = project
            uploaded_file.user = request.user
            uploaded_file.datetime = timezone.now()
            uploaded_file.save()
            # Build and send email message to all users on project besides
            # the user who uploaded
            project_users = [user for user in project.users.exclude(id=request.user.id)]
            for pu in project_users:
                context = {
                    'file_name': uploaded_file.readable_file_name(),
                    'project_name': project.name,
                    'user': pu,
                    'datetime': uploaded_file.datetime,
                    'uploaded_by': uploaded_file.user
                }
                template = get_template('email_notification.html')
                html = template.render(context)
                subject = 'A new file has been uploaded to %s' % project.name
                mail = EmailMultiAlternatives(
                    subject,
                    html,
                    'filecabinetapp@gmail.com',
                    [],
                    [pu.email]
                )
                mail.content_subtype = 'html'
                mail.send()
            messages.success(
                request, '%s has been successfully uploaded.' % (
                    uploaded_file.readable_file_name()
                )
            )
            return redirect('/uploader/'+str(project.id))
    if project:
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
            # If page is out of range (e.g. 9999) deliver last page of results.
            project_files = paginator.page(paginator.num_pages)
        return render(request, 'uploader.html', {
            'project': project,
            'projects': projects,
            'form': form,
            'project_files': project_files,
            'revisions': revisions,
            'revision': revision,
            'search_term': search,
            'recently_uploaded': recently_uploaded,
            'uploader': True
        })
    try:
        user_activity = UserActivity.objects.get(user=request.user)
        return redirect('/uploader/'+str(user_activity.last_project.id))
    except UserActivity.DoesNotExist:
        pass
    return render(request, 'uploader.html', {
        'selected_project': project,
        'projects': projects,
        'uploader': True
    })

@login_required
def get_project(request):
    project = request.POST['project']
    if project:
        obj, created = UserActivity.objects.update_or_create(
            user=request.user,
            defaults={'last_project_id': project}
        )
    else:
        UserActivity.objects.get(user=request.user).delete()
    return redirect('/uploader/'+project)

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
def update_profile(request, project=None):
    form = EditProfileForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email
    })
    try:
        project = Project.objects.get(pk=project)
        form_save_redirect = '/uploader/'+str(project.id)
    except Project.DoesNotExist:
        form_save_redirect = '/'
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            messages.info(request, 'User profile has been updated.')
            return redirect(form_save_redirect)

    return render(request, 'update_profile.html', {
        'user': request.user,
        'form': form,
        'project': project
    })

@login_required
def delete_file(request, project, file):
    UploadedFile.objects.get(pk=file).delete()
    return redirect('/uploader/')

@login_required
def get_or_create_project(request, project=None):
    # TODO clean this up, this prevents a user editing url then editing any
    # project
    if project:
        req_project = Project.objects.get(pk=project)

        if not req_project.created_by == request.user:
            messages.info(request,
                'You do not have permission to edit that project.'
            )
            return redirect('/')
    if request.method == 'POST':
        # If posted form has a current project than it is an 'edit'
        try:
            # TODO: fix
            new_proj_flag = False
            curr_proj = Project.objects.get(pk=project)
            form = ProjectForm(
                request.POST, instance=curr_proj, user=request.user)
            messages.info(
                request, 'Project %s has been updated.' % curr_proj.name)
        # If posted form does not have current project then it is a new project
        except Project.DoesNotExist:
            # TODO: fix
            new_proj_flag = True
            form = ProjectForm(request.POST, user=request.user)
            messages.info(
                request, 'Project %s has been created.' % request.POST['name'])
        if form.is_valid():
            project = form.save()
            project.users.add(request.user)
            if new_proj_flag:
                project.created_by = request.user
            project.save()
            obj, created = UserActivity.objects.update_or_create(
                user=request.user,
                defaults={'last_project_id': project.id}
            )
            # Redirect to main page showing new project
            return redirect('/uploader/'+str(project.id))
        return render(request, 'manage_project.html', {
            'form': form,
            'project': project
        })
    else:
        # If not project that means new project so render blank form
        form = ProjectForm(user=request.user)
        # If project comes in that means they are editing the project so
        # show the form with selected project info filled in
        if project:
            curr_proj = Project.objects.get(pk=project)
            form = ProjectForm(instance=curr_proj, user=request.user)
            return render(request, 'manage_project.html', {
                'form': form,
                'project': project,
                'curr_proj': curr_proj
            })
        return render(request, 'manage_project.html', {
            'form': form,
            'project': project
        })

@login_required
def delete_project(request, project):
    orig_proj = Project.objects.get(pk=project)
    Project.objects.get(pk=project).delete()
    messages.success(
        request, '%s has been permanently deleted.' % orig_proj.name)
    return redirect('/uploader/')

@login_required
def get_file(request, id):
    file = UploadedFile.objects.get(pk=id)
    path = file.file.name
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type='application/force-download'
            )
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        raise Http404
