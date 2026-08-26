from django.contrib import admin
from .models import Patient, Provider


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_number", "first_name", "last_name", "gender", "date_of_birth", "phone_number", "created_at")
    search_fields = ("patient_number", "first_name", "last_name", "phone_number")
    list_filter = ("gender",)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "license_number", "specialty", "department")
    search_fields = ("license_number", "user__first_name", "user__last_name")
