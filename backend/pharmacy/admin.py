from django.contrib import admin
from .models import Medication, Prescription, DispensingRecord

admin.site.register(Medication)
admin.site.register(Prescription)
admin.site.register(DispensingRecord)
