from django.shortcuts import render
from django.http import HttpResponse

from notes.models import Note


# Create your views here.

def home(request):

    notes = Note.objects.all()

    context = {
        'notes': notes,
        'total_notes': notes.count(),
    }

    return render(request, 'notes/home_page.html', context)
