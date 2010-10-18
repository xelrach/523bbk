from django.db import models
import hashlib

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.IntegerField()
    status = models.CharField(max_length=25)
    sha256 = models.CharField(max_length=64)

    def check_password(self, password):
        m = hashlib.sha256()
        m.update(password)
        return m.hexdigest() == self.sha256

class Event(models.Model):
    title = models.CharField(max_length=300)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField()

