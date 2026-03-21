from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('doctor', 'Doctor'),
        ('salon', 'Salon'),
        ('consult', 'Consultancy'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    duration = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


from django.db import models
from django.contrib.auth.models import User

class Appointment(models.Model):

    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('online', 'Online'),
    )

    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE)

    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')

    def __str__(self):
        return self.user.username
