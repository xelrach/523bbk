from django.db import models

class User(models.model):
    first_name = models.charField(max_length=100)
    last_name = modles.charField(max_length=100)
    email = modles.charField(max_length=100)
    phone = modles.intField()


class Event(models.model):
    title = models.charField(max_length=300)
    start = models.dateTime()
    end = models.dateTime()
    description = models.textField()

