from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import CanRegisterPatients
from core.models import AuditLog
from .models import Patient, Provider
from .serializers import PatientSerializer, ProviderSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    /api/patients/patients/
    Full CRUD for patient registration (Module 1). Read: any
    authenticated staff. Write: Admin tier + Nurse only (CanRegisterPatients).
    Every create/update/delete is written to the audit log.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, CanRegisterPatients]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["patient_number", "first_name", "last_name", "phone_number"]
    ordering_fields = ["created_at", "last_name", "date_of_birth"]

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user, action=AuditLog.Action.CREATE,
            entity_type="Patient", entity_id=str(instance.id),
            description=f"Registered patient {instance.patient_number}",
            ip_address=self._client_ip(),
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user, action=AuditLog.Action.UPDATE,
            entity_type="Patient", entity_id=str(instance.id),
            description=f"Updated patient {instance.patient_number}",
            ip_address=self._client_ip(),
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user, action=AuditLog.Action.DELETE,
            entity_type="Patient", entity_id=str(instance.id),
            description=f"Deleted patient {instance.patient_number}",
            ip_address=self._client_ip(),
        )
        instance.delete()

    def _client_ip(self):
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        return forwarded.split(",")[0] if forwarded else self.request.META.get("REMOTE_ADDR")


class ProviderViewSet(viewsets.ModelViewSet):
    """/api/patients/providers/ — admin tier manages provider credential records."""
    queryset = Provider.objects.select_related("user", "department").all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated, CanRegisterPatients]
