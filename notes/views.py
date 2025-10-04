from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from notes.forms import *
from notes.models import *


@sync_to_async
def filter_and_get_notes(user, search_query=None, category=None):
    notes_qs = Note.objects.filter(user=user).select_related('category')

    if search_query:
        notes_qs = notes_qs.filter(title__icontains=search_query)

    if category:
        notes_qs = notes_qs.filter(category=category)

    return list(notes_qs)


@sync_to_async
def get_note_or_404(note_id, user):
    try:
        return Note.objects.select_related('category').get(id=note_id, user=user)
    except ObjectDoesNotExist:
        raise Http404("Note not found")


@sync_to_async
def create_note_from_form(form, user):
    note = form.save(commit=False)
    note.user = user
    note.save()
    return note


@sync_to_async
def update_note_from_form(form):
    return form.save()


@sync_to_async
def delete_note_object(note):
    note.delete()


@sync_to_async
def create_category_from_form(form, user):
    category = form.save(commit=False)
    category.user = user
    category.save()
    return category


@login_required
async def home(request):

    search_form = await sync_to_async(SearchForm)(request.GET)
    filter_form = await sync_to_async(lambda: FilterForm(request.GET, user=request.user))()

    search_valid = await sync_to_async(search_form.is_valid)()
    filter_valid = await sync_to_async(filter_form.is_valid)()

    search_query = None
    category = None

    if search_valid:
        search_query = search_form.cleaned_data.get('search_query')

    if filter_valid:
        category = filter_form.cleaned_data.get('category')

    notes = await filter_and_get_notes(request.user, search_query, category)

    context = {
        'notes': notes,
        'total_notes': len(notes),
        'search': search_form,
        'filter': filter_form,
    }

    return await sync_to_async(render)(request, 'notes/home_page.html', context)


@login_required
async def create_note(request):

    if request.method == "POST":

        form = await sync_to_async(lambda: NoteForm(request.POST, user=request.user))()
        is_valid = await sync_to_async(form.is_valid)()

        if is_valid:
            await create_note_from_form(form, request.user)
            await sync_to_async(messages.success)(request, 'Нотатку успішно створено!')
            return redirect('home')
    else:
        form = await sync_to_async(lambda: NoteForm(user=request.user))()

    context = {
        'form': form,
        'title': 'Створити нотатку'
    }

    return await sync_to_async(render)(request, 'notes/note_form.html', context)


@login_required
async def note_detail(request, note_id):

    note = await get_note_or_404(note_id, request.user)

    context = {
        'note': note,
    }

    return await sync_to_async(render)(request, 'notes/note_detail.html', context)


@login_required
async def edit_note(request, note_id):

    note = await get_note_or_404(note_id, request.user)

    if request.method == "POST":
        form = await sync_to_async(lambda: NoteForm(request.POST, instance=note, user=request.user))()
        is_valid = await sync_to_async(form.is_valid)()

        if is_valid:
            await update_note_from_form(form)
            await sync_to_async(messages.success)(request, 'Нотатку оновлено!')
            return redirect('note_detail', note_id=note_id)
    else:
        form = await sync_to_async(lambda: NoteForm(instance=note, user=request.user))()

    context = {
        'form': form,
        'note': note,
        'title': 'Редагувати нотатку'
    }

    return await sync_to_async(render)(request, 'notes/note_form.html', context)


@login_required
async def delete_note(request, note_id):

    note = await get_note_or_404(note_id, request.user)

    if request.method == "POST":
        await delete_note_object(note)
        await sync_to_async(messages.success)(request, 'Нотатку видалено!')
        return redirect('home')

    context = {
        'note': note,
    }

    return await sync_to_async(render)(request, 'notes/note_delete.html', context)


@login_required
async def create_category(request):

    if request.method == "POST":
        form = await sync_to_async(lambda: CategoryForm(request.POST, user=request.user))()
        is_valid = await sync_to_async(form.is_valid)()

        if is_valid:
            await create_category_from_form(form, request.user)
            await sync_to_async(messages.success)(request, "Категорію створено!")
            return redirect('home')
    else:
        form = await sync_to_async(lambda: CategoryForm(user=request.user))()

    context = {
        'form': form,
    }

    return await sync_to_async(render)(request, 'notes/category_form.html', context)
