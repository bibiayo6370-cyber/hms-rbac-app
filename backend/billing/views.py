from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import CanManageBilling
from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    /api/billing/invoices/
    Billing and Payment module (Module 5). All authenticated staff may
    view billing status (e.g. a Doctor checking whether a patient has
    settled up), but only Billing Officer (and admin tier) can create
    or edit an invoice — CanManageBilling enforces this.
    """
    queryset = Invoice.objects.select_related("patient", "encounter").prefetch_related("payments").all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, CanManageBilling]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("invoice").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, CanManageBilling]
