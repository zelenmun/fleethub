from rest_framework import serializers
from apps.core.models import (Company, Address, Vehicle)
from django.utils import timezone
from datetime import timedelta

# # # SERIALIZADORES DEL MODELO COMPANY # # #

class CompanySerializer(serializers.ModelSerializer):
    """Serializer para el modelo Company."""

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'subdomain', 'legal_name', 'tax_id',
            'phone', 'email', 'daily_fee', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_subdomain(self, value):
        """Validar que el subdominio sea único y tenga formato válido."""
        # Convertir a minúsculas y validar formato
        value = value.lower().strip()

        if not value.replace('-', '').isalnum():
            raise serializers.ValidationError(
                "El subdominio solo puede contener letras, números y guiones."
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                "El subdominio debe tener al menos 3 caracteres."
            )

        return value

    def validate_tax_id(self, value):
        """Validar formato de RUC/identificación tributaria."""
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "La identificación tributaria debe tener al menos 10 dígitos."
            )

        return value

class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de Company."""

    class Meta:
        model = Company
        fields = [
            'name', 'subdomain', 'legal_name', 'tax_id',
            'phone', 'email', 'daily_fee'
        ]

    def validate_subdomain(self, value):
        """Validar que el subdominio sea único y tenga formato válido."""
        value = value.lower().strip()

        if not value.replace('-', '').isalnum():
            raise serializers.ValidationError(
                "El subdominio solo puede contener letras, números y guiones."
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                "El subdominio debe tener al menos 3 caracteres."
            )

        # Verificar que no existe
        if Company.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError(
                "Ya existe una compañía con este subdominio."
            )

        return value