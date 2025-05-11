from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet
from property.views import PropertyViewSet, UnitViewSet, AmenityViewSet, RentAdjustmentViewSet
from lease.views import LeaseViewSet
from invoices.views import InvoiceViewSet
from django.contrib import admin
from django.urls import path, include

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"property", PropertyViewSet, basename="property")
router.register(r"unit", UnitViewSet, basename="unit")
router.register(r"amenity", AmenityViewSet, basename='amenity')
router.register(r"adjustment", RentAdjustmentViewSet, basename="adjustment")
router.register(r"lease", LeaseViewSet, basename="lease")
router.register(r"invoice", InvoiceViewSet, basename="invoice")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
