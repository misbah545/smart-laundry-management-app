from django.contrib import admin
from .models import User, CustomerProfile, DriverProfile

admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(DriverProfile)
