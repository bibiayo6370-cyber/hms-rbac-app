from django.contrib import admin
from .models import Encounter, Diagnosis, Allergy, Observation, Appointment

admin.site.register(Encounter)
admin.site.register(Diagnosis)
admin.site.register(Allergy)
admin.site.register(Observation)
admin.site.register(Appointment)
