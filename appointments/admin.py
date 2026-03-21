from django.contrib import admin
from .models import Service, TimeSlot, Appointment

admin.site.register(Service)
admin.site.register(TimeSlot)
admin.site.register(Appointment)

# Register your models here.
