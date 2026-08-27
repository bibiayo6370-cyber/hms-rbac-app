from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsClinicalStaff, CanDispenseMedication
from .models import Medication, Prescription, DispensingRecord
from .serializers import MedicationSerializer, PrescriptionSerializer, DispensingRecordSerializer


class MedicationViewSet(viewsets.ModelViewSet):
    """Formulary catalogue — Admin tier and Pharmacist manage stock; everyone reads."""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated, CanDispenseMedication]


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    /api/pharmacy/prescriptions/
    Doctor writes a prescription (clinical act). Pharmacist reads it to
    fulfil, but does NOT create/edit prescriptions — enforced by
    IsClinicalStaff here, mirrored by CanDispenseMedication on the
    DispensingRecord endpoint below.
    """
    queryset = Prescription.objects.select_related("encounter", "medication").all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class DispensingRecordViewSet(viewsets.ModelViewSet):
    """
    /api/pharmacy/dispensing-records/
    Only Pharmacist may create a dispensing record — the other half of
    the prescribe/dispense separation-of-duties boundary.
    """
    queryset = DispensingRecord.objects.select_related("prescription").all()
    serializer_class = DispensingRecordSerializer
    permission_classes = [IsAuthenticated, CanDispenseMedication]
