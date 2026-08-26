import uuid
from django.conf import settings
from django.db import models


class LaboratoryOrder(models.Model):
    """Laboratory_Order — maps to FHIR ServiceRequest. Doctor -> Lab handoff."""
    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.CASCADE, related_name="lab_orders")
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="lab_orders_placed")
    test_name = models.CharField(max_length=150)
    loinc_code = models.CharField(max_length=20, blank=True, help_text="LOINC code, if available")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ORDERED)
    ordered_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-ordered_at"]

    def __str__(self):
        return f"Lab order: {self.test_name} for {self.encounter.patient} ({self.status})"


class LaboratoryResult(models.Model):
    """Laboratory_Result — maps to FHIR Observation/DiagnosticReport."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(LaboratoryOrder, on_delete=models.CASCADE, related_name="result")
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="lab_results_entered")
    result_value = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    is_abnormal = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    entered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.order.test_name}: {self.result_value} {self.unit}"
