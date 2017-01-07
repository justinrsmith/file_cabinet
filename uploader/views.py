from django.shortcuts import render, redirect
from uploader.forms import UploadedFileForm
from uploader.models import UploadedFile
from django.urls import reverse

# Create your views here.
def uploader(request):
    form = UploadedFileForm()
    files = UploadedFile.objects.all()
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
        'revisions': revisions
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
        'revisions': revisions
    })
