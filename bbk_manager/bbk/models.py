from django.db import models
import hashlib
import datetime

class Address(models.Model):
    line1 = models.CharField(max_length=100, default="")
    line2 = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    zip_code = models.CharField(max_length=7, default="")

class Application(models.Model):
    user = models.OneToOneField('User', related_name="application")
    former_names = models.CharField(max_length=255,default="")
    birthdate = models.DateField(null=True)
    experience = models.TextField(default="")
    skills = models.TextField(default="")
    involvement = models.TextField(default="")
    why = models.TextField(default="")
    how = models.TextField(default="")

class Checklist(models.Model):
    user = models.OneToOneField('User',related_name="checklist")
    confidential_form = models.BooleanField()
    background_check = models.BooleanField()
    vaccines = models.BooleanField()
    references = models.BooleanField()

class Phone(models.Model):
    number = models.CharField(max_length=20,default="")
    location = models.CharField(max_length=2,default="")

    def get_number(self, seperator="."):
        number = self.number
        if not number:
            return ""
        formatted = ""
        if len(number)==11:
            formatted += number[0]+seperator
            number = number[1:]
        if len(number)==10:
            formatted += number[0:3]+seperator
            number = number[3:]
        if len(number)==7:
            formatted += number[0:3]+seperator
            number = number[3:]
        return formatted + number

    def __unicode__(self):
        return self.get_number()

    def save(self,*args,**kwargs):
        import re
        self.number = re.sub(r'[^\d]','',self.number)
        super(Phone,self).save(*args,**kwargs)

class Reference(models.Model):
    name = models.CharField(max_length=100, default="")
    email = models.CharField(max_length=100, default="")
    phone = models.ForeignKey(Phone, null=True)
    address = models.ForeignKey(Address, null=True)
    application = models.ForeignKey(Application, related_name="references")

class User(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=10)
    address = models.ForeignKey(Address,null=True)
    email = models.CharField(max_length=100,unique=True)
    phones = models.ManyToManyField(Phone)
    status = models.CharField(max_length=25)
    sha256 = models.CharField(max_length=64)

    def check_password(self, password):
        m = hashlib.sha256()
        m.update(password)
        return m.hexdigest() == self.sha256

    def set_password(self, password):
        m = hashlib.sha256()
        m.update(password)
        self.sha256 = m.hexdigest()

class Event(models.Model):
    title = models.CharField(max_length=300)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(default="")
    message = models.TextField(default="")
    max_volunteers = models.IntegerField(default=10)
    volunteers = models.ManyToManyField(User, through="Signup")

class Signup(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = (("event", "user"),)
