from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.core.models import (Company, Address, Vehicle)
from apps.core.serializers.serializer_company import (CompanySerializer, CompanyCreateSerializer)

class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de compañías."""

    queryset = Company.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción."""
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer

    def perform_create(self, serializer):
        """Establecer el usuario que crea el registro."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Establecer el usuario que actualiza el registro."""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Eliminación lógica de la compañía."""
        company = self.get_object()
        company.soft_delete()
        return Response({
            'message': 'Compañía desactivada exitosamente.',
            'company_id': company.id
        })

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar compañía eliminada lógicamente."""
        company = get_object_or_404(Company, pk=pk)
        company.restore()
        return Response({
            'message': 'Compañía restaurada exitosamente.',
            'company_id': company.id
        })

    @action(detail=False, methods=['get'])
    def by_subdomain(self, request):
        """Obtener compañía por subdominio."""
        subdomain = request.query_params.get('subdomain')

        if not subdomain:
            return Response(
                {'error': 'Parámetro subdomain es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            company = Company.objects.get(subdomain=subdomain, is_active=True)
            serializer = self.get_serializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Compañía no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Estadísticas básicas de la compañía."""
        company = self.get_object()

        # Aquí puedes agregar más estadísticas cuando tengas otros módulos
        stats = {
            'company_name': company.name,
            'daily_fee': company.daily_fee,
            'created_at': company.created_at,
            'is_active': company.is_active,
            # Cuando implementes otros módulos, agregas:
            # 'total_vehicles': company.vehicle_set.filter(is_active=True).count(),
            # 'total_shareholders': company.shareholder_set.filter(is_active=True).count(),
        }

        return Response(stats)