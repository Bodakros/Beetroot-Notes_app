from django.db import models

# Create your models here.



class Note(models.Model):
    title = models.CharField(max_length=100, help_text='Name of your note')
    text = models.TextField(blank=True, help_text='Text of your note (Can be blank)')
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    reminder = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"


class Category(models.Model):
    title = models.CharField(max_length=100, help_text='Name of your category', unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ('title', 'user')
