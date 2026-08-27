from rest_framework.routers import DefaultRouter
from .views import LaboratoryOrderViewSet, LaboratoryResultViewSet

router = DefaultRouter()
router.register("orders", LaboratoryOrderViewSet, basename="lab-order")
router.register("results", LaboratoryResultViewSet, basename="lab-result")

urlpatterns = router.urls
