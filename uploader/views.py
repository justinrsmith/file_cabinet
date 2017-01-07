from django.shortcuts import render, redirect
from uploader.forms import UploadedFileForm
from uploader.models import UploadedFile
from django.urls import reverse

# Create your views here.
def uploader(request):
    form = UploadedFileForm()
    files = UploadedFile.objects.all()

    if request.method == 'POST':
        #TODO: request.FILES?
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('uploader'))

    return render(request, 'uploader.html', {
        'form': form,
        'files': files
    })
