from django.contrib.auth.decorators import login_required
from django.contrib.messages.context_processors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from notes.forms import *
from notes.models import *


# Create your views here.
@login_required
def home(request):

    notes = Note.objects.filter(user=request.user)
    search_form = SearchForm(request.GET)
    filter_form = FilterForm(request.GET, user=request.user)

    if search_form.is_valid() and search_form.cleaned_data['search_query']:
        search_query = search_form.cleaned_data['search_query']
        notes = notes.filter(title__icontains=search_query)

    if filter_form.is_valid() and filter_form.cleaned_data['category']:
        category = filter_form.cleaned_data['category']
        notes = notes.filter(category=category)

    context = {
        'notes': notes,
        'total_notes': notes.count(),
        'search': search_form,
        'filter': filter_form,
    }

    return render(request, 'notes/home_page.html', context)


@login_required
def create_note(request):

    if request.method == "POST":
        form = NoteForm(request.POST, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Нотатку успішно створено!')
            return redirect('home')
    else:
        form = NoteForm(user=request.user)

    context = {
        'form': form,
        'title': 'Створити нотатку'
    }

    return render(request, 'notes/note_form.html', context)


@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)

    context = {
        'note': note,
    }

    return render(request, 'notes/note_detail.html', context)


@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Нотатку оновлено!')
            return redirect('note_detail', note_id=note_id)
    else:
        form = NoteForm(instance=note, user=request.user)

    context = {
        'form': form,
        'note': note,
        'title': 'Редагувати нотатку'
    }

    return  render(request, 'notes/note_form.html', context)


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, 'Нотатку видалено!')
        return redirect('home')

    context = {
        'note': note,
    }

    return  render(request, 'notes/note_delete.html', context)


@login_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Категорію створено!")
            return redirect('home')
    else:
        form = CategoryForm(user=request.user)

    context = {
        'form': form,
    }
    return  render(request, 'notes/category_form.html', context)
