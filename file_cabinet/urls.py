"""file_cabinet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, static, include
from django.contrib import admin
from uploader import views as uploader_views
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Authorization urls

    #  Register
    url(r'^registration/$', uploader_views.register_user, name='registration'),
    #  Login
    url(r'^$', uploader_views.login_view, name='login'),
    #  Logut
    url(r'^logout/$', uploader_views.logout_view, name='logout'),
    #  Edit profile
    url(r'^update_profile/$', uploader_views.update_profile, name='update_profile'),
    url(r'^update_profile/(?P<project>[0-9]+)/$', uploader_views.update_profile, name='update_profile'),
    #  Pasword reset email form (django built in), with custom template #TODO: style??
    url(
        r'password_reset/$',  auth_views.password_reset, {
            'template_name': 'password_reset_form.html'
        }, name='password_reset'
    ),
    #  Pasword reset success/action notice (django built in)
    url
        (r'password_reset_done/$', auth_views.password_reset_done, {
            'template_name': 'password_reset_done.html'
        }, name='password_reset_done'),
    #  Pasword reset form (django built in)
    url(
        r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {
            'template_name': 'password_reset_confirm.html'
        }, name='password_reset_confirm'
    ),
    #  Change notice and return to login link
    url(r'reset/done/$', auth_views.password_reset_complete,  {
            'template_name': 'password_reset_complete.html'
            }, name='password_reset_complete'
    ),
    # App urls

    #  main app view
    url(r'^uploader/$', uploader_views.uploader, name='uploader'),
    #  feed in project
    url(r'^uploader/(?P<project>[0-9]+)/$', uploader_views.uploader, name='uploader'),
    #  feed in project and revision
    url(r'^uploader/(?P<project>[0-9]+)/(?P<revision>[0-9]+)/$', uploader_views.uploader, name='uploader'),
    #  feed in project and search term
    url(r'^uploader/(?P<project>[0-9]+)/(?P<search>[\w\-]+)/$', uploader_views.uploader, name='uploader'),
    #  feed in project and revision and search term
    url(r'^uploader/(?P<project>[0-9]+)/(?P<revision>[0-9]+)/(?P<search>[\w\-]+)/$', uploader_views.uploader, name='uploader'),
    #  view to redirect to selected project (TODO)
    url(r'^uploader/get_project/$', uploader_views.get_project, name='get_project'),
    #  view to redirect to selected project and revision for projects (TODO)
    url(r'^uploader/get_revision/(?P<project>[0-9]+)/$', uploader_views.get_revision, name='get_revision'),
    #  view to redirect to selected project and revision for projects (TODO)
    url(r'^uploader/get_revision/(?P<project>[0-9]+)/(?P<search>[\w\-]+)/$', uploader_views.get_revision, name='get_revision'),
    #  view to redirect to selected project and search term for projects (TODO)
    url(r'^uploader/get_search/(?P<project>[0-9]+)/$', uploader_views.get_search, name='get_search'),
    #  view to redirect to selected project and revision and search term for projects (TODO)
    url(r'^uploader/get_search/(?P<project>[0-9]+)/(?P<revision>[0-9]+)/$', uploader_views.get_search, name='get_search'),
    #  view to delete seclected file (TODO)
    url(r'^uploader/delete/(?P<project>[0-9]+)/(?P<file>[0-9]+)/$', uploader_views.delete_file, name='delete_file'),
    #  add a project
    url(r'^uploader/add_project/', uploader_views.get_or_create_project, name='get_or_create_project'),
    url(r'^uploader/edit_project/(?P<project>[0-9]+)/', uploader_views.get_or_create_project, name='get_or_create_project'),
    url(r'^uploader/get_file/(?P<id>[0-9]+)', uploader_views.get_file, name='get_file'),
    url(r'^uploader/delete_project/(?P<project>[0-9]+)/', uploader_views.delete_project, name='delete_project'),
    #get_or_create_project
]  + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
