import uuid
from django.conf import settings
from django.db import models


class Invoice(models.Model):
    """Invoice — aggregates consultation fees, lab charges, and pharmacy costs."""
    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="invoices")
    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.SET_NULL, null=True, related_name="invoices")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    laboratory_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pharmacy_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="invoices_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_amount(self):
        return (
            self.consultation_fee + self.laboratory_charges
            + self.pharmacy_charges + self.other_charges
        )

    @property
    def amount_paid(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            year = timezone.now().year
            count = Invoice.objects.filter(created_at__year=year).count() + 1
            self.invoice_number = f"INV-{year}-{count:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — {self.patient} ({self.status})"


class Payment(models.Model):
    """Payment — one or more payments applied against an Invoice."""
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        TRANSFER = "TRANSFER", "Bank Transfer"
        INSURANCE = "INSURANCE", "Insurance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="payments_received")
    paid_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"
