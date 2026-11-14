from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "patient", "doctor", "status")
    list_filter = ("status", "doctor", "date")
