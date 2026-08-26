from django.contrib import admin
from .models import LaboratoryOrder, LaboratoryResult

admin.site.register(LaboratoryOrder)
admin.site.register(LaboratoryResult)
