from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.IntegerField()
    status = models.CharField(max_length=25)

class Event(models.Model):
    title = models.CharField(max_length=300)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField()

