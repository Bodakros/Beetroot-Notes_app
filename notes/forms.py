from django import forms
from .models import *


class NoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(NoteForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)

    class Meta:
        model = Note
        fields = ['title', 'text', 'category', 'reminder']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть назву нотатки',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть текст нотатки',
                'rows': 5
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reminder': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            })
        }
        labels = {
            'title': 'Назва нотатки',
            'text': 'Текст нотатки',
            'category': 'Категорія',
            'reminder': 'Нагадування'
        }

class CategoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.user:
            existing = Category.objects.filter(title=title, user=self.user)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError("Категорія з такою назвою вже існує.")
        return title

    class Meta:
        model = Category
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть назву категорії'
            })
        }
        labels = {
            'title': 'Назва категорії'
        }

class SearchForm(forms.Form):

    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук по назві...'
        }),
        label="Пошук"
    )


class FilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        else:
            self.fields['category'].queryset = Category.objects.none()

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='Всі категорії',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Категорія'
    )
