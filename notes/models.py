from django.db import models

# Create your models here.



class Note(models.Model):
    title = models.CharField(max_length=100, help_text='Name of your note')
    text = models.TextField(blank=True, help_text='Text of your note (Can be blank)')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
