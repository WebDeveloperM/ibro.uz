from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    definition = models.TextField()
    pronunciation = models.CharField(max_length=100, blank=True)
    letter_count = models.PositiveIntegerField()
    categories = models.ManyToManyField(Category, related_name='words', blank=True)
    search_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # 🔹 so‘zlar sonini avtomatik hisoblash
        self.letter_count = len(self.word.replace(" ", ""))

        # 🔹 slug avtomatik
        if not self.slug:
            self.slug = slugify(self.word)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.word
