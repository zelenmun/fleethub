from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.views.views_address import (AddressViewSet)
from apps.core.views.views_company import (CompanyViewSet)
from apps.core.views.views_vehicle import (VehicleViewSet)

# Crear el router para las APIs REST
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'vehicles', VehicleViewSet)

urlpatterns = [
    # API REST endpoints
    path('api/', include(router.urls)),
]

