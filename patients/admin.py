from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("mrn", "full_name", "national_id", "gender", "phone")
    search_fields = ("mrn", "first_name", "last_name", "national_id")
