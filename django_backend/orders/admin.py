from django.contrib import admin
from .models import Order, Cloth, DriverLocation

admin.site.register(Order)
admin.site.register(Cloth)
admin.site.register(DriverLocation)
