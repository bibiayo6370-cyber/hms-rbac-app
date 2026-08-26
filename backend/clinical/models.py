import uuid
from django.conf import settings
from django.db import models


class Encounter(models.Model):
    """Doctor Consultation module — Encounter maps to FHIR Encounter."""
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="encounters")
    provider = models.ForeignKey("patients.Provider", on_delete=models.SET_NULL, null=True, related_name="encounters")
    department = models.ForeignKey("core.Department", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    chief_complaint = models.TextField(help_text="Presenting complaint")
    examination_findings = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Encounter {self.id} — {self.patient} ({self.status})"


class Diagnosis(models.Model):
    """Diagnosis/Condition — first-class coded concept (Section 3.4.1), not free text."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="diagnoses")
    description = models.CharField(max_length=255)
    icd10_code = models.CharField(max_length=10, blank=True, help_text="ICD-10 code, if available")
    is_primary = models.BooleanField(default=False)
    diagnosed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.icd10_code or 'UNCODED'}: {self.description}"


class Allergy(models.Model):
    """Allergy/Adverse Reaction — patient-safety element (Section 3.4.1)."""
    class Severity(models.TextChoices):
        MILD = "MILD", "Mild"
        MODERATE = "MODERATE", "Moderate"
        SEVERE = "SEVERE", "Severe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="allergies")
    substance = models.CharField(max_length=150)
    reaction = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MODERATE)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} allergic to {self.substance} ({self.severity})"


class Observation(models.Model):
    """Vital Signs/Observation — nursing observations captured during an encounter."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="observations")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    pulse_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vitals for {self.encounter.patient} at {self.recorded_at:%Y-%m-%d %H:%M}"


class Appointment(models.Model):
    """Appointment — scheduling concept (Section 3.4.1)."""
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CHECKED_IN = "CHECKED_IN", "Checked In"
        COMPLETED = "COMPLETED", "Completed"
        NO_SHOW = "NO_SHOW", "No Show"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="appointments")
    provider = models.ForeignKey("patients.Provider", on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey("core.Department", on_delete=models.SET_NULL, null=True)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_for"]

    def __str__(self):
        return f"Appt: {self.patient} on {self.scheduled_for:%Y-%m-%d %H:%M}"
