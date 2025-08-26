from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.core.models import (Address)
from apps.core.serializers.serializer_address import (AddressSerializer, AddressCreateSerializer, AddressListSerializer)

# Importar Cities Light models
try:
    from cities_light.models import Country, Region, City, SubRegion

    CITIES_LIGHT_AVAILABLE = True
except ImportError:
    CITIES_LIGHT_AVAILABLE = False


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de direcciones."""

    queryset = Address.objects.filter(is_active=True)

    # permission_classes = [IsAuthenticated]  # Comentado para pruebas

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción."""
        if self.action == 'create':
            return AddressCreateSerializer
        elif self.action == 'list':
            return AddressListSerializer
        return AddressSerializer

    def get_queryset(self):
        """Filtrar direcciones por parámetros."""
        queryset = self.queryset

        # Filtrar por tipo de contenido
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type__model=content_type)

        # Filtrar por objeto específico
        object_id = self.request.query_params.get('object_id')
        if object_id:
            queryset = queryset.filter(object_id=object_id)

        # Filtrar por ciudad
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        return queryset

    def perform_create(self, serializer):
        """Establecer el usuario que crea el registro."""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Establecer el usuario que actualiza el registro."""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Eliminación lógica de la dirección."""
        address = self.get_object()
        address.soft_delete()
        return Response({
            'message': 'Dirección desactivada exitosamente.',
            'address_id': address.id
        })

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar dirección eliminada lógicamente."""
        address = get_object_or_404(Address, pk=pk)
        address.restore()
        return Response({
            'message': 'Dirección restaurada exitosamente.',
            'address_id': address.id
        })

    # ===========================================
    # ENDPOINTS PARA CITIES LIGHT (SELECTS)
    # ===========================================

    @action(detail=False, methods=['get'])
    def countries(self, request):
        """Obtener lista de países para selects."""
        if not CITIES_LIGHT_AVAILABLE:
            return Response(
                {'error': 'Cities Light no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        countries = Country.objects.all().order_by('name')
        data = [{'id': c.id, 'name': c.name, 'code': c.code2} for c in countries]

        return Response(data)

    @action(detail=False, methods=['get'])
    def regions(self, request):
        """Obtener provincias filtradas por país."""
        if not CITIES_LIGHT_AVAILABLE:
            return Response(
                {'error': 'Cities Light no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        country_id = request.query_params.get('country_id')
        if not country_id:
            return Response(
                {'error': 'Parámetro country_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            regions = Region.objects.filter(country_id=country_id).order_by('name')
            data = [{'id': r.id, 'name': r.name} for r in regions]
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error al obtener regiones: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def cities(self, request):
        """Obtener ciudades filtradas por provincia."""
        if not CITIES_LIGHT_AVAILABLE:
            return Response(
                {'error': 'Cities Light no está disponible.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        region_id = request.query_params.get('region_id')
        if not region_id:
            return Response(
                {'error': 'Parámetro region_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cities = City.objects.filter(region_id=region_id).order_by('name')
            data = [{'id': c.id, 'name': c.name} for c in cities]
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error al obtener ciudades: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )