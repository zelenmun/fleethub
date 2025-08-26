from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta

from apps.core.models import (Vehicle)
from apps.core.serializers.serializer_vehicle import (VehicleSerializer, VehicleCreateSerializer, VehicleListSerializer,
                                                      VehicleStatusUpdateSerializer)

class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de vehículos."""

    queryset = Vehicle.objects.filter(is_active=True)

    # permission_classes = [IsAuthenticated]  # Comentado para pruebas

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción."""
        if self.action == 'create':
            return VehicleCreateSerializer
        elif self.action == 'list':
            return VehicleListSerializer
        elif self.action == 'update_status':
            return VehicleStatusUpdateSerializer
        return VehicleSerializer

    def get_queryset(self):
        """Filtrar vehículos por parámetros."""
        queryset = self.queryset.select_related('company')

        # Filtrar por compañía
        company_id = self.request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filtrar por placa (búsqueda parcial)
        license_plate = self.request.query_params.get('license_plate')
        if license_plate:
            queryset = queryset.filter(license_plate__icontains=license_plate.upper())

        # Filtrar por marca
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        # Filtrar por año
        year = self.request.query_params.get('year')
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except ValueError:
                pass

        # Filtrar vehículos con documentos próximos a vencer
        expiring_soon = self.request.query_params.get('expiring_soon')
        if expiring_soon:
            alert_date = timezone.now().date() + timedelta(days=30)
            queryset = queryset.filter(
                Q(soat_expiry__lte=alert_date) |
                Q(technical_review_expiry__lte=alert_date) |
                Q(operation_permit_expiry__lte=alert_date)
            )

        return queryset.order_by('-created_at')

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
        """Eliminación lógica del vehículo."""
        vehicle = self.get_object()
        vehicle.soft_delete()
        return Response({
            'message': 'Vehículo desactivado exitosamente.',
            'vehicle_id': vehicle.id,
            'license_plate': vehicle.license_plate
        })

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar vehículo eliminado lógicamente."""
        vehicle = get_object_or_404(Vehicle, pk=pk)
        vehicle.restore()
        return Response({
            'message': 'Vehículo restaurado exitosamente.',
            'vehicle_id': vehicle.id,
            'license_plate': vehicle.license_plate
        })

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Actualizar estado del vehículo."""
        vehicle = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'instance': vehicle}
        )

        if serializer.is_valid():
            old_status = vehicle.status
            new_status = serializer.validated_data['status']
            reason = serializer.validated_data.get('reason', '')

            vehicle.status = new_status
            vehicle.status_changed_at = timezone.now()

            if hasattr(request, 'user') and request.user.is_authenticated:
                vehicle.updated_by = request.user

            vehicle.save()

            return Response({
                'message': f'Estado cambiado de {old_status} a {new_status}.',
                'vehicle_id': vehicle.id,
                'license_plate': vehicle.license_plate,
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason,
                'changed_at': vehicle.status_changed_at
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Búsqueda avanzada de vehículos."""
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response(
                {'error': 'Parámetro de búsqueda "q" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar en múltiples campos
        vehicles = self.get_queryset().filter(
            Q(license_plate__icontains=query) |
            Q(chassis_number__icontains=query) |
            Q(identifier_number__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query) |
            Q(engine_number__icontains=query)
        )[:20]  # Limitar a 20 resultados

        serializer = VehicleListSerializer(vehicles, many=True)

        return Response({
            'query': query,
            'count': vehicles.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        """Vehículos con documentos próximos a vencer."""
        days = int(request.query_params.get('days', 30))
        alert_date = timezone.now().date() + timedelta(days=days)
        today = timezone.now().date()

        vehicles = self.get_queryset().filter(
            Q(soat_expiry__lte=alert_date) |
            Q(technical_review_expiry__lte=alert_date) |
            Q(operation_permit_expiry__lte=alert_date)
        )

        expired = vehicles.filter(
            Q(soat_expiry__lt=today) |
            Q(technical_review_expiry__lt=today) |
            Q(operation_permit_expiry__lt=today)
        )

        expiring = vehicles.filter(
            Q(soat_expiry__range=[today, alert_date]) |
            Q(technical_review_expiry__range=[today, alert_date]) |
            Q(operation_permit_expiry__range=[today, alert_date])
        ).exclude(pk__in=expired)

        return Response({
            'alert_days': days,
            'expired_count': expired.count(),
            'expiring_count': expiring.count(),
            'expired_vehicles': VehicleListSerializer(expired, many=True).data,
            'expiring_vehicles': VehicleListSerializer(expiring, many=True).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de vehículos."""
        queryset = self.get_queryset()

        # Estadísticas por estado
        status_stats = queryset.values('status').annotate(count=Count('id'))

        # Estadísticas por marca
        brand_stats = queryset.values('brand').annotate(count=Count('id')).order_by('-count')[:10]

        # Estadísticas por año
        year_stats = queryset.values('year').annotate(count=Count('id')).order_by('-year')

        # Documentos vencidos
        today = timezone.now().date()
        expired_soat = queryset.filter(soat_expiry__lt=today).count()
        expired_technical = queryset.filter(technical_review_expiry__lt=today).count()
        expired_permits = queryset.filter(operation_permit_expiry__lt=today).count()

        return Response({
            'total_vehicles': queryset.count(),
            'status_breakdown': {item['status']: item['count'] for item in status_stats},
            'top_brands': list(brand_stats),
            'by_year': list(year_stats),
            'expired_documents': {
                'soat': expired_soat,
                'technical_review': expired_technical,
                'operation_permits': expired_permits
            }
        })

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """Información completa del vehículo con alertas."""
        vehicle = self.get_object()
        serializer = self.get_serializer(vehicle)

        # Información adicional
        today = timezone.now().date()
        alerts = []

        # Verificar vencimientos
        if vehicle.soat_expiry:
            if vehicle.soat_expiry < today:
                alerts.append({'type': 'error', 'message': 'SOAT vencido'})
            elif (vehicle.soat_expiry - today).days <= 30:
                days_left = (vehicle.soat_expiry - today).days
                alerts.append({'type': 'warning', 'message': f'SOAT vence en {days_left} días'})

        if vehicle.technical_review_expiry:
            if vehicle.technical_review_expiry < today:
                alerts.append({'type': 'error', 'message': 'Revisión técnica vencida'})
            elif (vehicle.technical_review_expiry - today).days <= 30:
                days_left = (vehicle.technical_review_expiry - today).days
                alerts.append({'type': 'warning', 'message': f'Revisión técnica vence en {days_left} días'})

        if vehicle.operation_permit_expiry:
            if vehicle.operation_permit_expiry < today:
                alerts.append({'type': 'error', 'message': 'Permiso de operación vencido'})
            elif (vehicle.operation_permit_expiry - today).days <= 30:
                days_left = (vehicle.operation_permit_expiry - today).days
                alerts.append({'type': 'warning', 'message': f'Permiso de operación vence en {days_left} días'})

        response_data = serializer.data
        response_data['alerts'] = alerts

        return Response(response_data)

