from django.contrib import admin

from .models import Saloon, Procedure, Master

admin.site.register(Saloon)
admin.site.register(Procedure)
admin.site.register(Master)