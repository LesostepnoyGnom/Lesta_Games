from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Main(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    user_name = models.CharField(max_length=255)
    top_word = models.CharField(max_length=255)
    time_processed = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    text_size = models.IntegerField()

    def __str__(self):
        return self.top_word

class Documents(models.Model):
    doc_name = models.CharField(max_length=255)
    user_id = models.IntegerField(null=True, blank=True)
    collection_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.doc_name

class Collection(models.Model):
    collection_name = models.CharField(max_length=255)
    user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.collection_name