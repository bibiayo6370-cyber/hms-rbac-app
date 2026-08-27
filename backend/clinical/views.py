from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsClinicalStaff
from .models import Encounter, Diagnosis, Allergy, Observation, Appointment
from .serializers import (
    EncounterSerializer, DiagnosisSerializer, AllergySerializer,
    ObservationSerializer, AppointmentSerializer,
)


class EncounterViewSet(viewsets.ModelViewSet):
    """
    /api/clinical/encounters/
    Doctor Consultation module (Module 2). Write access: Doctor, Nurse
    (IsClinicalStaff) — this is the peer boundary Lab Tech, Pharmacist,
    and Billing Officer must NOT cross.
    """
    queryset = Encounter.objects.select_related("patient", "provider", "department").all()
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.select_related("encounter").all()
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class AllergyViewSet(viewsets.ModelViewSet):
    queryset = Allergy.objects.select_related("patient").all()
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.select_related("encounter").all()
    serializer_class = ObservationSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class AppointmentViewSet(viewsets.ModelViewSet):
    """Scheduling — Admin tier and clinical staff can manage appointments."""
    queryset = Appointment.objects.select_related("patient", "provider", "department").all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]
