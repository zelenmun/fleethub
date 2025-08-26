from rest_framework import serializers
from apps.core.models import (Company, Address, Vehicle)
from django.utils import timezone
from datetime import timedelta

# # # SERIALIZADORES DEL MODELO ADDRESS # # #

class AddressSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Address."""

    # Campo calculado para mostrar dirección completa
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = [
            'id', 'country', 'province', 'city', 'sector',
            'postal_code', 'reference', 'content_type', 'object_id',
            'full_address', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_address']

    def get_full_address(self, obj):
        """Generar dirección completa legible."""
        parts = []

        if obj.sector:
            parts.append(obj.sector)
        if obj.city:
            parts.append(obj.city)
        if obj.province:
            parts.append(obj.province)
        if obj.country:
            parts.append(obj.country)

        return ", ".join(parts)

    def validate(self, attrs):
        """Validaciones personalizadas."""
        # Validar que al menos ciudad y provincia estén presentes
        if not attrs.get('city') or not attrs.get('province'):
            raise serializers.ValidationError(
                "Ciudad y provincia son campos obligatorios."
            )

        return attrs

class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de direcciones."""

    class Meta:
        model = Address
        fields = [
            'country', 'province', 'city', 'sector',
            'postal_code', 'reference', 'content_type', 'object_id'
        ]

    def validate_country(self, value):
        """Validar que el país existe en Cities Light."""
        # Aquí puedes agregar validación contra cities_light_country si quieres
        return value.strip().title()

    def validate_province(self, value):
        """Validar formato de provincia."""
        return value.strip().title()

    def validate_city(self, value):
        """Validar formato de ciudad."""
        return value.strip().title()

class AddressListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados."""

    full_address = serializers.SerializerMethodField()
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = [
            'id', 'full_address', 'related_object', 'created_at'
        ]

    def get_full_address(self, obj):
        """Dirección completa para listados."""
        parts = [obj.city, obj.province, obj.country]
        return ", ".join(filter(None, parts))

    def get_related_object(self, obj):
        """Información del objeto relacionado."""
        if obj.content_object:
            return {
                'type': obj.content_type.model,
                'name': str(obj.content_object)
            }
        return None