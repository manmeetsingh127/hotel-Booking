from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Hotel(models.Model):
    hotelId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(default=None, null=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    roomId = models.AutoField(primary_key=True)
    roomType = models.CharField(max_length=100)
    hotelId = models.IntegerField()
    price = models.FloatField()
    available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.roomType


class Reservation(models.Model):
    hotelId = models.IntegerField()
    hotelName = models.CharField(max_length=100, default=None)
    customerName = models.CharField(max_length=100)
    roomId = models.IntegerField()
    accountId = models.IntegerField()
    date = models.CharField(max_length=100)

    def __str__(self):
        string = "room:"+str(self.roomId)+"| date:"+str(self.date)
        return string

class Waitlist(models.Model):
    waitlistId = models.AutoField(primary_key=True)
    hotelId = models.IntegerField()
    roomId = models.IntegerField()
    accountId = models.IntegerField()
    customerName = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=(('pending','pending'),('confirmed','confirmed')),
                              default="pending")

    def __str__(self):
        string = "room:"+str(self.roomId)+"| date:"+str(self.date)
        return string

ACCOUNT_CHOICES = (
    ("customer", "Customer"),
    ("employee", "Employee")
)


class Account(models.Model):
    accountId = models.AutoField(primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    accountType = models.CharField(max_length=100, choices=ACCOUNT_CHOICES,
                                   default="Customer")
    rewardPoints = models.PositiveIntegerField(blank=True, null=True, default=0)
    salary = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.email
