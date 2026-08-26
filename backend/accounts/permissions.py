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


class HasRole(BasePermission):
    """
    Generic factory-style permission: grants access only if the
    requesting user's role is in the allowed set. Super Admins always
    pass, matching the hierarchical administrative tier in Section 3.3.2.
    """
    def __init__(self, *allowed_roles):
        self.allowed_roles = set(allowed_roles)

    def __call__(self):
        # DRF instantiates permission_classes; this lets HasRole(...) be
        # used directly in the permission_classes list.
        return self

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.role == Role.SUPER_ADMIN:
            return True
        return user.role in self.allowed_roles


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


class ReadOnlyOrIsAdminTier(BasePermission):
    """Any authenticated user may GET/HEAD/OPTIONS; only admin tier may write."""
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return user.role in (Role.SUPER_ADMIN, Role.ADMIN)
