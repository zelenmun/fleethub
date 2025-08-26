from rest_framework import serializers
from apps.core.models import (Company, Address, Vehicle)
from django.utils import timezone
from datetime import timedelta

# # # SERIALIZADORES DEL MODELO VEHICLE # # #


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Vehicle."""

    # Campos calculados
    days_until_soat_expiry = serializers.SerializerMethodField()
    days_until_technical_review_expiry = serializers.SerializerMethodField()
    days_until_operation_permit_expiry = serializers.SerializerMethodField()
    vehicle_age = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Información de la compañía
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'company', 'company_name', 'identifier_number', 'license_plate',
            'chassis_number', 'engine_number', 'brand', 'model', 'year', 'color',
            'engine_displacement', 'passenger_capacity', 'status', 'status_display',
            'status_changed_at', 'soat_expiry', 'technical_review_expiry',
            'operation_permit_expiry', 'days_until_soat_expiry',
            'days_until_technical_review_expiry', 'days_until_operation_permit_expiry',
            'vehicle_age', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'status_changed_at',
            'company_name', 'status_display'
        ]

    def get_days_until_soat_expiry(self, obj):
        """Calcular días hasta vencimiento del SOAT."""
        if not obj.soat_expiry:
            return None

        today = timezone.now().date()
        days = (obj.soat_expiry - today).days
        return days

    def get_days_until_technical_review_expiry(self, obj):
        """Calcular días hasta vencimiento de revisión técnica."""
        if not obj.technical_review_expiry:
            return None

        today = timezone.now().date()
        days = (obj.technical_review_expiry - today).days
        return days

    def get_days_until_operation_permit_expiry(self, obj):
        """Calcular días hasta vencimiento del permiso de operación."""
        if not obj.operation_permit_expiry:
            return None

        today = timezone.now().date()
        days = (obj.operation_permit_expiry - today).days
        return days

    def get_vehicle_age(self, obj):
        """Calcular edad del vehículo en años."""
        current_year = timezone.now().year
        return current_year - obj.year

    def validate_year(self, value):
        """Validar que el año sea razonable."""
        current_year = timezone.now().year

        if value < 1990:
            raise serializers.ValidationError(
                "El año no puede ser anterior a 1990."
            )

        if value > current_year + 1:
            raise serializers.ValidationError(
                f"El año no puede ser posterior a {current_year + 1}."
            )

        return value

    def validate_engine_displacement(self, value):
        """Validar cilindraje razonable para tricimotos."""
        if value < 50 or value > 500:
            raise serializers.ValidationError(
                "El cilindraje debe estar entre 50cc y 500cc para tricimotos."
            )

        return value

    def validate_passenger_capacity(self, value):
        """Validar capacidad de pasajeros."""
        if value < 1 or value > 6:
            raise serializers.ValidationError(
                "La capacidad debe estar entre 1 y 6 pasajeros."
            )

        return value

class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de vehículos."""

    class Meta:
        model = Vehicle
        fields = [
            'company', 'identifier_number', 'license_plate', 'chassis_number',
            'engine_number', 'brand', 'model', 'year', 'color',
            'engine_displacement', 'passenger_capacity', 'soat_expiry',
            'technical_review_expiry', 'operation_permit_expiry'
        ]

    def validate_license_plate(self, value):
        """Validar formato de placa ecuatoriana."""
        value = value.upper().strip()

        # Formato básico: ABC-1234 (3 letras, guión, 4 números)
        if len(value) != 8 or value[3] != '-':
            raise serializers.ValidationError(
                "Formato de placa inválido. Use: ABC-1234"
            )

        letters = value[:3]
        numbers = value[4:]

        if not letters.isalpha() or not numbers.isdigit():
            raise serializers.ValidationError(
                "La placa debe tener 3 letras seguidas de guión y 4 números."
            )

        return value

    def validate(self, attrs):
        """Validaciones cruzadas."""
        company = attrs.get('company')
        license_plate = attrs.get('license_plate')
        chassis_number = attrs.get('chassis_number')
        identifier_number = attrs.get('identifier_number')

        # Verificar unicidad dentro de la compañía
        if company:
            if Vehicle.objects.filter(company=company, license_plate=license_plate).exists():
                raise serializers.ValidationError(
                    "Ya existe un vehículo con esta placa en la compañía."
                )

            if Vehicle.objects.filter(company=company, chassis_number=chassis_number).exists():
                raise serializers.ValidationError(
                    "Ya existe un vehículo con este número de chasis en la compañía."
                )

            if Vehicle.objects.filter(company=company, identifier_number=identifier_number).exists():
                raise serializers.ValidationError(
                    "Ya existe un vehículo con este número identificador en la compañía."
                )

        return attrs

class VehicleListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    alert_status = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'license_plate', 'vehicle_info', 'status', 'status_display',
            'alert_status', 'created_at'
        ]

    def get_vehicle_info(self, obj):
        """Información resumida del vehículo."""
        return f"{obj.brand} {obj.model} ({obj.year})"

    def get_alert_status(self, obj):
        """Estado de alertas por vencimientos."""
        today = timezone.now().date()
        alert_threshold = today + timedelta(days=30)  # 30 días de alerta

        alerts = []

        if obj.soat_expiry and obj.soat_expiry <= alert_threshold:
            if obj.soat_expiry < today:
                alerts.append("SOAT vencido")
            else:
                alerts.append("SOAT próximo a vencer")

        if obj.technical_review_expiry and obj.technical_review_expiry <= alert_threshold:
            if obj.technical_review_expiry < today:
                alerts.append("Revisión técnica vencida")
            else:
                alerts.append("Revisión técnica próxima a vencer")

        if obj.operation_permit_expiry and obj.operation_permit_expiry <= alert_threshold:
            if obj.operation_permit_expiry < today:
                alerts.append("Permiso vencido")
            else:
                alerts.append("Permiso próximo a vencer")

        return alerts

class VehicleStatusUpdateSerializer(serializers.Serializer):
    """Serializer para actualización de estado del vehículo."""

    status = serializers.ChoiceField(choices=Vehicle.STATUS_CHOICES)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_status(self, value):
        """Validar transiciones de estado permitidas."""
        instance = self.context.get('instance')

        if not instance:
            return value

        current_status = instance.status

        # Definir transiciones permitidas
        allowed_transitions = {
            'active': ['suspended', 'revoked'],
            'suspended': ['active', 'revoked'],
            'revoked': []  # Una vez revocado, no se puede cambiar
        }

        if current_status == 'revoked' and value != 'revoked':
            raise serializers.ValidationError(
                "No se puede cambiar el estado de un vehículo revocado."
            )

        if value not in allowed_transitions.get(current_status, []) and value != current_status:
            raise serializers.ValidationError(
                f"No se puede cambiar de {current_status} a {value}."
            )

        return value