import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """
    The six user roles defined in Chapter 3, Section 3.3.2 (RBAC Architecture).
    Administrative roles (SUPER_ADMIN, ADMIN) are hierarchical.
    Professional roles (DOCTOR, NURSE, LAB_TECH, PHARMACIST) are independent
    peers and do not inherit from one another.
    BILLING_OFFICER owns billing/payment functions.
    """
    SUPER_ADMIN = "SUPER_ADMIN", "Super Administrator"
    ADMIN = "ADMIN", "Administrative Staff"
    DOCTOR = "DOCTOR", "Doctor"
    NURSE = "NURSE", "Nurse"
    LAB_TECH = "LAB_TECH", "Laboratory Technician"
    PHARMACIST = "PHARMACIST", "Pharmacist"
    BILLING_OFFICER = "BILLING_OFFICER", "Billing Officer"


class User(AbstractUser):
    """
    Custom user model. Extends Django's AbstractUser so we keep
    battle-tested auth (password hashing, permissions scaffolding)
    while adding the `role` field that drives RBAC across the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.NURSE)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        "core.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="staff"
    )
    is_active_staff = models.BooleanField(
        default=True,
        help_text="Soft-disable a staff account without deleting it."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # --- Convenience role checks used throughout the codebase ---
    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN

    @property
    def is_admin_tier(self):
        return self.role in (Role.SUPER_ADMIN, Role.ADMIN)

    @property
    def is_clinical(self):
        return self.role in (Role.DOCTOR, Role.NURSE)
