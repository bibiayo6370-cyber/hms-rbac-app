import uuid
from django.conf import settings
from django.db import models


class Medication(models.Model):
    """Medication/Formulary — controlled catalogue that prescriptions reference."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    strength = models.CharField(max_length=50, blank=True, help_text="e.g. 500mg")
    form = models.CharField(max_length=50, blank=True, help_text="e.g. Tablet, Syrup, Injection")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} {self.strength}".strip()


class Prescription(models.Model):
    """Prescription — maps to FHIR MedicationRequest."""
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DISPENSED = "DISPENSED", "Dispensed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.CASCADE, related_name="prescriptions")
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, related_name="prescriptions")
    prescribed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="prescriptions_written")
    dosage_instructions = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    prescribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rx: {self.medication} x{self.quantity} for {self.encounter.patient}"


class DispensingRecord(models.Model):
    """Dispensing_Record — pharmacist fulfilling a prescription."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name="dispensing_record")
    dispensed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="dispensations")
    quantity_dispensed = models.PositiveIntegerField()
    dispensed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Dispensed {self.quantity_dispensed} of {self.prescription.medication}"
