from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_note, name='create_note'),
    path('<int:note_id>/', views.note_detail, name='note_detail'),
    path('<int:note_id>/edit/', views.edit_note, name='edit_note'),
    path('<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('category/create/', views.create_category, name='create_category'),
]
