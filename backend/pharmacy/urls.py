from rest_framework.routers import DefaultRouter
from .views import MedicationViewSet, PrescriptionViewSet, DispensingRecordViewSet

router = DefaultRouter()
router.register("medications", MedicationViewSet, basename="medication")
router.register("prescriptions", PrescriptionViewSet, basename="prescription")
router.register("dispensing-records", DispensingRecordViewSet, basename="dispensing-record")

urlpatterns = router.urls
