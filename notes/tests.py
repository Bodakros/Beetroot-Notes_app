from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import *
from .forms import *
from .views import *


class NoteModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(title="Test Category")
        self.note = Note.objects.create(
            title="Test Note",
            text="This is a test note.",
            category=self.category,
            reminder=timezone.now()
        )

    def test_note_full_creation(self):
        self.assertEqual(self.note.title, "Test Note")
        self.assertEqual(self.note.text, "This is a test note.")
        self.assertEqual(self.note.category.title, "Test Category")
        self.assertIsNotNone(self.note.reminder)


    def test_note_creation_without_text_reminder(self):
        note = Note.objects.create(
            title="Note without text and reminder",
            category=self.category
        )
        self.assertEqual(note.text, "")
        self.assertIsNone(note.reminder)

    def test_validation_error_on_missing_title(self):
        note = Note(title="", category=self.category)
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_validation_error_on_missing_category(self):
        note = Note(title="Test", category=None)
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_category_association(self):
        self.assertEqual(self.note.category.title, "Test Category")

    def test_note_title_max_length(self):
        max_length = self.note._meta.get_field('title').max_length
        self.assertEqual(max_length, 100)

    def test_note_str_representation(self):
        self.assertEqual(str(self.note), "Test Note")

    def test_category_verbose_names(self):
        self.assertEqual(Note._meta.verbose_name, "Note")
        self.assertEqual(Note._meta.verbose_name_plural, "Notes")

    def test_category_relationship(self):
        self.assertEqual(self.note.category, self.category)
        self.assertIn(self.note, self.category.note_set.all())

    def test_note_protect_on_delete(self):
        with self.assertRaises(Exception):
            self.category.delete()
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())

    def test_different_notes_same_category(self):
        note2 = Note.objects.create(
            title="Second Note",
            text="This is another test note.",
            category=self.category
        )
        self.assertEqual(note2.category, self.category)
        self.assertIn(note2, self.category.note_set.all())

    def test_note_change_category(self):
        new_category = Category.objects.create(title="New Category")
        self.note.category = new_category
        self.note.save()
        self.assertEqual(self.note.category, new_category)
        self.assertIn(self.note, new_category.note_set.all())
        self.assertNotIn(self.note, self.category.note_set.all())

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test Category")

    def test_unique_category_names(self):
        with self.assertRaises(Exception):
            Category.objects.create(title="Test Category")

    def test_category_str_representation(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_category_title_max_length(self):
        max_length = self.category._meta.get_field('title').max_length
        self.assertEqual(max_length, 100)

    def test_category_verbose_names(self):
        self.assertEqual(Category._meta.verbose_name, "Category")
        self.assertEqual(Category._meta.verbose_name_plural, "Categories")


class NoteFormTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(title="Test Category")
        self.valid_data = {
            'title': 'Test Note',
            'text': 'This is a test note.',
            'category': self.category.id,
            'reminder': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }

    def test_note_form_valid_data_all_field(self):
        form = NoteForm(data=self.valid_data)
        note = form.save()

        self.assertTrue(form.is_valid())
        self.assertEqual(note.title, 'Test Note')
        self.assertIsNotNone(note.reminder)

    def test_note_form_with_minimal_fields(self):
        minimal_data = {
            'title': 'Minimal Note',
            'category': self.category.id,
        }
        form = NoteForm(data=minimal_data)
        note = form.save()

        self.assertTrue(form.is_valid())
        self.assertEqual(note.title, 'Minimal Note')
        self.assertEqual(note.text, '')
        self.assertIsNone(note.reminder)

    def test_note_form_missing_title(self):
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = ''
        form = NoteForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_widgets_and_labels(self):
        form = NoteForm()
        self.assertIn('class="form-control"', str(form['title']))
        self.assertIn('placeholder="Введіть назву нотатки"', str(form['title']))
        self.assertEqual(form.fields['title'].label, 'Назва нотатки')

        self.assertIn('class="form-control"', str(form['text']))
        self.assertIn('placeholder="Введіть текст нотатки"', str(form['text']))
        self.assertEqual(form.fields['text'].label, 'Текст нотатки')

        self.assertIn('class="form-control"', str(form['category']))
        self.assertEqual(form.fields['category'].label, 'Категорія')

        self.assertIn('class="form-control"', str(form['reminder']))
        self.assertIn('type="datetime-local"', str(form['reminder']))
        self.assertEqual(form.fields['reminder'].label, 'Нагадування')


class CategoryFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'title': 'Test Category'
        }

    def test_category_form_valid_data(self):
        form = CategoryForm(data=self.valid_data)
        category = form.save()

        self.assertTrue(form.is_valid())
        self.assertEqual(category.title, 'Test Category')

    def test_category_form_missing_title(self):
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = ''
        form = CategoryForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_unique_category_names(self):
        Category.objects.create(title="Unique Category")
        duplicate_data = {
            'title': 'Unique Category'
        }
        form = CategoryForm(data=duplicate_data)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_widgets_and_labels(self):
        form = CategoryForm()
        self.assertIn('class="form-control"', str(form['title']))
        self.assertIn('placeholder="Введіть назву категорії"', str(form['title']))
        self.assertEqual(form.fields['title'].label, 'Назва категорії')


class SearchFormTest(TestCase):

    def test_search_form_empty_query(self):
        form = SearchForm(data={'search_query': ''})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search_query'], '')

    def test_search_form_valid_query(self):
        form = SearchForm(data={'search_query': 'Test'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search_query'], 'Test')

    def test_search_form_exceeding_max_length(self):
        long_query = 'a' * 101
        form = SearchForm(data={'search_query': long_query})
        self.assertFalse(form.is_valid())
        self.assertIn('search_query', form.errors)

    def test_form_widgets_and_labels(self):
        form = SearchForm()
        self.assertIn('class="form-control"', str(form['search_query']))
        self.assertIn('placeholder="Пошук по назві..."', str(form['search_query']))
        self.assertEqual(form.fields['search_query'].label, 'Пошук')


class FilterFormTest(TestCase):

    def setUp(self):
        self.category1 = Category.objects.create(title="Category 1")
        self.category2 = Category.objects.create(title="Category 2")

    def test_filter_form_no_selection(self):
        form = FilterForm(data={'category': ''})
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['category'])

    def test_filter_form_valid_selection(self):
        form = FilterForm(data={'category': self.category1.id})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['category'], self.category1)

        form = FilterForm(data={'category': self.category2.id})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['category'], self.category2)

    def test_form_widgets_and_labels(self):
        form = FilterForm()
        self.assertIn('class="form-control"', str(form['category']))
        self.assertEqual(form.fields['category'].label, 'Категорія')


class NoteViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(title="Test Category")
        self.data = {
            'title': 'New Note',
            'text': 'This is a new note.',
            'category': self.category.id,
            'reminder': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        self.updated_data = {
            'title': 'Updated Note',
            'text': 'This note has been updated.',
            'category': self.category.id,
            'reminder': ''
        }

        self.note = Note.objects.create(
            title="Test Note",
            text="This is a test note.",
            category=self.category,
            reminder=timezone.now()
        )

    # home view tests
    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/home_page.html')
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    # create_note view tests
    def test_create_note_view_get(self):
        url = reverse('create_note')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')

    def test_create_note_view_post_valid(self):
        url = reverse('create_note')
        response = self.client.post(url, self.data)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='New Note').exists())
        self.assertEqual(Note.objects.get(title='New Note').text, 'This is a new note.')

    def test_create_note_view_post_invalid(self):
        url = reverse('create_note')
        bad_data = self.data.copy()
        del bad_data['category']

        response = self.client.post(url, bad_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')
        self.assertFalse(Note.objects.filter(text='This is a new note.').exists())

    # note_detail view tests
    def test_note_detail_view(self):
        url = reverse('note_detail', args=[self.note.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_detail.html')
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_note_detail_view_not_found(self):
        url = reverse('note_detail', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # edit_note view tests
    def test_edit_note_view_get(self):
        url = reverse('edit_note', args=[self.note.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_edit_note_view_post_valid(self):
        url = reverse('edit_note', args=[self.note.id])
        response = self.client.post(url, self.updated_data)

        self.assertRedirects(response, reverse('note_detail', args=[self.note.id]))
        self.assertEqual(response.status_code, 302)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.text, 'This note has been updated.')

    def test_edit_note_view_post_invalid(self):
        url = reverse('edit_note', args=[self.note.id])
        up_data = self.updated_data.copy()
        del up_data['category']

        response = self.client.post(url, up_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_form.html')
        self.assertNotEqual(self.note.title, 'Updated Note')

    def test_edit_note_view_not_found(self):
        url = reverse('edit_note', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # delete_note view tests
    def test_delete_note_view_get(self):
        url = reverse('delete_note', args=[self.note.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_delete.html')
        self.assertContains(response, self.note.title)

    def test_delete_note_view_post(self):
        url = reverse('delete_note', args=[self.note.id])
        response = self.client.post(url)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_delete_note_view_not_found(self):
        url = reverse('delete_note', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # create_category view tests
    def test_create_category_view_get(self):
        url = reverse('create_category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/category_form.html')

    def test_create_category_view_post_valid(self):
        url = reverse('create_category')
        data = {'title': 'New Category'}
        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(title='New Category').exists())

    def test_create_category_view_post_invalid(self):
        url = reverse('create_category')
        data = {'title': 'New Category'}
        data2 = {'title': 'New Category'}
        response = self.client.post(url, data)
        response2 = self.client.post(url, data2)

        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, 'notes/category_form.html')
        self.assertFormError(response2.context['form'], 'title',
                             'Category with this Title already exists.')

    # Search and Filter tests
    def test_search_functionality(self):
        url = reverse('create_note')
        response = self.client.post(url, self.data)

        url = reverse('home')
        response = self.client.get(url, {'search_query': 'New'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New")
        self.assertNotContains(response, 'Test Note')

    def test_filter_functionality(self):
        category2 = Category.objects.create(title="Another Category")
        url = reverse('create_note')
        data = self.data.copy()
        data['category'] = category2
        response = self.client.post(url, data)

        url = reverse('home')
        response = self.client.get(url, {'category': self.category.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note.title)
        self.assertNotContains(response, 'New Note')

class IntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(title="Integration Category")
        self.data = {
            'title': 'New Note',
            'text': 'This is a new note.',
            'category': self.category.id,
            'reminder': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }

    def test_full_note_lifecycle(self):
        # Create
        create_url = reverse('create_note')
        response = self.client.post(create_url, self.data)
        self.assertRedirects(response, reverse('home'))
        note = Note.objects.get(title='New Note')

        # Read
        detail_url = reverse('note_detail', args=[note.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Note')

        # Update
        edit_url = reverse('edit_note', args=[note.id])
        updated_data = self.data.copy()
        updated_data['title'] = 'Updated Note'
        response = self.client.post(edit_url, updated_data)
        self.assertRedirects(response, reverse('note_detail', args=[note.id]))
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Note')

        # Delete
        delete_url = reverse('delete_note', args=[note.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Note.objects.filter(id=note.id).exists())
