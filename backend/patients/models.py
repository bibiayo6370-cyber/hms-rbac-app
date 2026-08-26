import uuid
from django.conf import settings
from django.db import models


class Patient(models.Model):
    """
    Patient entity. Maps to the FHIR Patient resource (Section 2.3.4)
    for future interoperability.
    """
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_number = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text="System-assigned unique patient identifier (FR: patient registration)."
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    next_of_kin_name = models.CharField(max_length=150, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="patients_registered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["patient_number"]),
        ]

    def save(self, *args, **kwargs):
        if not self.patient_number:
            self.patient_number = self._generate_patient_number()
        super().save(*args, **kwargs)

    def _generate_patient_number(self):
        from django.utils import timezone
        year = timezone.now().year
        count = Patient.objects.filter(created_at__year=year).count() + 1
        return f"PT-{year}-{count:05d}"

    def __str__(self):
        return f"{self.patient_number} — {self.first_name} {self.last_name}"


class Provider(models.Model):
    """
    Provider/Clinician entity (Section 3.4.1) — the credentialed
    professional who conducts an encounter, distinct from the generic
    system User (a Provider record is linked 1:1 to a User account).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="provider_profile"
    )
    license_number = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        "core.Department", on_delete=models.SET_NULL, null=True, related_name="providers"
    )

    def __str__(self):
        return f"Dr./Provider {self.user.get_full_name()} ({self.license_number})"
