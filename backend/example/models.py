from django.db import models

# Create your models here.
class Example(models.Model) :
  title = models.CharField(max_length=100)
  author = models.CharField(max_length=100)
  publication_date = models.DateField()
  price = models.IntegerField()

  class Meta:
      verbose_name = '도서'
      verbose_name_plural = '도서 목록'

  def __str__(self):
      return self.title