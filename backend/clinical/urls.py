from rest_framework.routers import DefaultRouter
from .views import EncounterViewSet, DiagnosisViewSet, AllergyViewSet, ObservationViewSet, AppointmentViewSet

router = DefaultRouter()
router.register("encounters", EncounterViewSet, basename="encounter")
router.register("diagnoses", DiagnosisViewSet, basename="diagnosis")
router.register("allergies", AllergyViewSet, basename="allergy")
router.register("observations", ObservationViewSet, basename="observation")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = router.urls
