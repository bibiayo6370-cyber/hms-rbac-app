from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ProviderViewSet

router = DefaultRouter()
router.register("patients", PatientViewSet, basename="patient")
router.register("providers", ProviderViewSet, basename="provider")

urlpatterns = router.urls
