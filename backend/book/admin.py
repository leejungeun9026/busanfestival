from django.contrib import admin
from .models import Book

# Register your models here.
class BookAdmin(admin.ModelAdmin):
  search_fields = ['title']

admin.site.register(Book, BookAdmin)