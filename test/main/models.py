from django.db import models
from django.utils import timezone

# Create your models here.

class Main(models.Model):
    top_word = models.CharField(max_length=255)
    time_processed = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    text_size = models.IntegerField()


    def __str__(self):
        return self.top_word