"""
DRF permission classes implementing the Role-Permission matrix described
in Chapter 3, Section 3.3.2. Access control is enforced HERE, at the API
layer, on every request — the frontend's conditional rendering (hiding
buttons/menus for a role) is a UX convenience only and must never be
relied on as the actual security boundary. Dual-layer enforcement means
even a manipulated frontend cannot bypass these checks.

Usage in a view:
    permission_classes = [IsAuthenticated, HasRole("DOCTOR", "NURSE")]
"""
from rest_framework.permissions import BasePermission
from .models import Role


def HasRole(*allowed_roles):
    """
    Factory that returns a genuine BasePermission SUBCLASS (not an
    instance), so it drops into permission_classes exactly the way DRF
    expects: DRF's get_permissions() does
        [permission() for permission in self.permission_classes]
    i.e. it instantiates each entry itself. Passing an already-built
    instance (the previous implementation) only worked by accident via
    a __call__ trick. This version returns a fresh class per call,
    which DRF instantiates normally — no special-casing required.

    Usage:
        permission_classes = [IsAuthenticated, HasRole(Role.DOCTOR, Role.NURSE)]

    Prefer the explicit named classes below (IsDoctor, IsClinicalStaff,
    etc.) for role combinations used repeatedly across views — they
    read as a direct, defensible mapping to the Role-Permission matrix
    in Section 3.3.2. Reach for HasRole(...) only for one-off view-
    specific combinations that don't deserve a permanent named class.
    """
    allowed = set(allowed_roles)

    class _HasRole(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            if not (user and user.is_authenticated):
                return False
            if user.role == Role.SUPER_ADMIN:
                return True
            return user.role in allowed

    return _HasRole


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.SUPER_ADMIN)


class IsAdminTier(BasePermission):
    """Super Administrator or Administrative Staff."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in (Role.SUPER_ADMIN, Role.ADMIN)
        )


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.DOCTOR)


class IsNurse(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.NURSE)


class IsLabTech(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.LAB_TECH)


class IsPharmacist(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.PHARMACIST)


class IsBillingOfficer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.BILLING_OFFICER)


class IsClinicalStaff(BasePermission):
    """Doctor or Nurse — used for endpoints both roles may read/write (e.g. Observations)."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in (Role.DOCTOR, Role.NURSE, Role.SUPER_ADMIN))


class CanWriteLabResults(BasePermission):
    """
    Only Lab Technicians may write laboratory results — this is the
    non-inheriting peer boundary from Section 3.3.2: Doctor and Nurse
    can each ORDER a test (via clinical write access) but neither may
    RECORD a result, that authority belongs solely to Lab Tech.
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return user.role in (
                Role.SUPER_ADMIN, Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.LAB_TECH
            )
        return user.role in (Role.SUPER_ADMIN, Role.LAB_TECH)


class CanDispenseMedication(BasePermission):
    """
    Only Pharmacists may create Dispensing_Records. Doctors write
    Prescriptions (clinical module) but cannot dispense — enforcing the
    prescribe/dispense separation-of-duties boundary in Section 3.3.2.
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return user.role in (
                Role.SUPER_ADMIN, Role.ADMIN, Role.DOCTOR, Role.PHARMACIST
            )
        return user.role in (Role.SUPER_ADMIN, Role.PHARMACIST)


class CanManageBilling(BasePermission):
    """Only the Billing Officer (and admin tier) may create/modify Invoices and Payments."""
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True  # any authenticated staff may view billing status
        return user.role in (Role.SUPER_ADMIN, Role.ADMIN, Role.BILLING_OFFICER)


class CanRegisterPatients(BasePermission):
    """
    Patient Registration module (Section 3.2.2, Module 1). Any
    authenticated staff member may look up patient records — clinical
    work depends on that — but only front-desk/admin staff and Nurses
    may create or edit a registration, matching real hospital workflow
    (a Lab Tech or Pharmacist has no business editing demographics).
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return user.role in (Role.SUPER_ADMIN, Role.ADMIN, Role.NURSE)


class ReadOnlyOrIsAdminTier(BasePermission):
    """Any authenticated user may GET/HEAD/OPTIONS; only admin tier may write."""
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return user.role in (Role.SUPER_ADMIN, Role.ADMIN)
