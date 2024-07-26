from django.contrib import admin

from .models import Client, Salon, Specialist,  Service, Order, SpecialistWorkDayInSalon, Appointment

admin.site.register(Client)
admin.site.register(Salon)
admin.site.register(Specialist)
admin.site.register(SpecialistWorkDayInSalon)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(Appointment)
