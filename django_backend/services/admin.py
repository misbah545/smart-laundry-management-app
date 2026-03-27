from django.contrib import admin
from .models import ChatbotLog, AIPrediction

admin.site.register(ChatbotLog)
admin.site.register(AIPrediction)

# Import advanced model admins
from .advanced_admin import *
