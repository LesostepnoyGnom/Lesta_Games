from django.db import models

# Create your models here.

class Main(models.Model):
    word = models.CharField(max_length=255)
    tf = models.IntegerField()
    idf = models.IntegerField()

    def __str__(self):
        return self.word

    class Meta:
        ordering = ["-idf"]