from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminTier
from billing.models import Invoice, Payment
from clinical.models import Encounter
from laboratory.models import LaboratoryOrder
from patients.models import Patient


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/

    Administrative Dashboard module (FR, Section 3.2.2):
    "The system shall provide an administrative dashboard that presents
    real-time metrics, including daily patient volume, department
    throughput, and revenue summary."

    Restricted to the admin tier (Super Administrator, Administrative
    Staff) via IsAdminTier — clinical/operational staff do not need
    hospital-wide financial and volume aggregates.
    """
    permission_classes = [IsAuthenticated, IsAdminTier]

    def get(self, request):
        today = timezone.now().date()
        last_7_days = today - timedelta(days=6)

        # Daily patient volume (registrations today, and a 7-day trend)
        patients_today = Patient.objects.filter(created_at__date=today).count()
        trend_qs = (
            Patient.objects.filter(created_at__date__gte=last_7_days)
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        patient_trend = list(trend_qs)

        # Department throughput: encounters per department, last 7 days
        throughput = (
            Encounter.objects.filter(started_at__date__gte=last_7_days)
            .values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Revenue summary
        revenue_today = (
            Payment.objects.filter(paid_at__date=today).aggregate(total=Sum("amount"))["total"] or 0
        )
        revenue_7_days = (
            Payment.objects.filter(paid_at__date__gte=last_7_days).aggregate(total=Sum("amount"))["total"] or 0
        )
        outstanding_invoices = Invoice.objects.exclude(
            status__in=[Invoice.Status.PAID, Invoice.Status.VOID]
        ).count()

        # Lab turnaround snapshot
        pending_lab_orders = LaboratoryOrder.objects.filter(
            status__in=[LaboratoryOrder.Status.ORDERED, LaboratoryOrder.Status.IN_PROGRESS]
        ).count()

        return Response({
            "generated_at": timezone.now(),
            "patient_volume": {
                "today": patients_today,
                "last_7_days_trend": patient_trend,
            },
            "department_throughput_7_days": list(throughput),
            "revenue": {
                "today": revenue_today,
                "last_7_days": revenue_7_days,
                "outstanding_invoices": outstanding_invoices,
            },
            "laboratory": {
                "pending_orders": pending_lab_orders,
            },
        })
