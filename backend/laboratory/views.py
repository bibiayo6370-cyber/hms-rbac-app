from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsClinicalStaff, CanWriteLabResults
from .models import LaboratoryOrder, LaboratoryResult
from .serializers import LaboratoryOrderSerializer, LaboratoryResultSerializer


class LaboratoryOrderViewSet(viewsets.ModelViewSet):
    """
    /api/laboratory/orders/
    Doctor/Nurse can CREATE an order (they request the test). Lab Tech
    can read all orders (to work the queue) and update status, but
    order *creation* stays with clinical staff — a Lab Tech doesn't
    originate the request, they fulfil it.
    """
    queryset = LaboratoryOrder.objects.select_related("encounter").all()
    serializer_class = LaboratoryOrderSerializer
    permission_classes = [IsAuthenticated, IsClinicalStaff]


class LaboratoryResultViewSet(viewsets.ModelViewSet):
    """
    /api/laboratory/results/
    This is the key peer boundary from Section 3.3.2: ONLY Lab Tech may
    write a result, even though Doctor/Nurse can read it. CanWriteLabResults
    enforces exactly this.
    """
    queryset = LaboratoryResult.objects.select_related("order").all()
    serializer_class = LaboratoryResultSerializer
    permission_classes = [IsAuthenticated, CanWriteLabResults]
