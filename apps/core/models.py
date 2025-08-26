import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils import timezone

class BaseModel(models.Model):
    """Modelo base abstracto con campos comunes de auditoría y gestión."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Identificador único universal")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de creación")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha y hora de última actualización")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_created", help_text="Usuario que creó el registro")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_updated", help_text="Usuario que actualizó el registro")
    is_active = models.BooleanField(default=True, help_text="Indica si el registro está activo")

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class TenantBaseModel(BaseModel):
    """Modelo base abstracto para entidades multi-tenant ligadas a una compañía."""
    company = models.ForeignKey('Company', on_delete=models.CASCADE, help_text="Compañía a la que pertenece este registro")

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['company', 'is_active'])]


class Company(BaseModel):
    """Modelo de compañía para multi-tenancy."""
    name = models.CharField(max_length=200, help_text="Nombre comercial de la compañía")
    subdomain = models.CharField(max_length=50, unique=True, db_index=True, help_text="Subdominio multi-tenant")
    legal_name = models.CharField(max_length=300, help_text="Razón social de la compañía")
    tax_id = models.CharField(max_length=20, unique=True, help_text="RUC o identificación tributaria")
    phone = models.CharField(max_length=15, blank=True, help_text="Teléfono de contacto")
    email = models.EmailField(blank=True, help_text="Email de contacto")
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Tarifa diaria cobrada a socios")
    addresses = GenericRelation('Address', help_text="Direcciones asociadas a esta compañía")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Compañía"
        verbose_name_plural = "Compañías"


class Person(TenantBaseModel):
    """Modelo abstracto base para personas en el sistema."""
    first_name = models.CharField(max_length=100, help_text="Nombres")
    last_name = models.CharField(max_length=100, help_text="Apellidos")
    document_type = models.CharField(max_length=20, choices=[('cedula', 'Cédula'), ('passport', 'Pasaporte'), ('ruc', 'RUC')], default='cedula', help_text="Tipo de documento de identidad")
    document_number = models.CharField(max_length=20, help_text="Número de documento de identidad")
    phone = models.CharField(max_length=15, blank=True, help_text="Número de teléfono")
    email = models.EmailField(blank=True, help_text="Correo electrónico")
    birth_date = models.DateField(null=True, blank=True, help_text="Fecha de nacimiento")
    addresses = GenericRelation('Address', help_text="Direcciones asociadas a esta persona")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name

    class Meta:
        abstract = True
        unique_together = ['company', 'document_number']


class Address(BaseModel):
    """Direcciones reutilizables y polimórficas en el sistema."""
    country = models.CharField(max_length=50, default='Ecuador', help_text="País")
    province = models.CharField(max_length=100, help_text="Provincia")
    city = models.CharField(max_length=100, help_text="Ciudad")
    sector = models.CharField(max_length=100, null=True, blank=True, help_text="Sector o barrio")
    postal_code = models.CharField(max_length=10, null=True, blank=True, help_text="Código postal")
    reference = models.CharField(max_length=500, help_text="Referencia o indicaciones adicionales", blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, help_text="Tipo de modelo al que pertenece esta dirección")
    object_id = models.UUIDField(help_text="ID del objeto al que pertenece esta dirección")
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.city}, {self.province} - {self.content_object}"

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"


class Vehicle(TenantBaseModel):
    """Modelo de vehículos (tricimotos) del sistema."""
    STATUS_CHOICES = [('active', 'Activo'), ('suspended', 'Suspendido'), ('revoked', 'Revocado')]

    identifier_number = models.CharField(max_length=50, help_text="Número identificador único del vehículo")
    license_plate = models.CharField(max_length=10, help_text="Placa del vehículo")
    chassis_number = models.CharField(max_length=50, help_text="Número de chasis")
    engine_number = models.CharField(max_length=50, blank=True, help_text="Número de motor")
    brand = models.CharField(max_length=50, help_text="Marca del vehículo")
    model = models.CharField(max_length=50, help_text="Modelo del vehículo")
    year = models.PositiveIntegerField(help_text="Año de fabricación")
    color = models.CharField(max_length=30, help_text="Color del vehículo")
    engine_displacement = models.PositiveIntegerField(help_text="Cilindraje en CC")
    passenger_capacity = models.PositiveIntegerField(default=3, help_text="Capacidad de pasajeros")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', help_text="Estado del vehículo")
    status_changed_at = models.DateTimeField(auto_now_add=True, help_text="Fecha del último cambio de estado")
    soat_expiry = models.DateField(null=True, blank=True, help_text="Fecha de vencimiento del SOAT")
    technical_review_expiry = models.DateField(null=True, blank=True, help_text="Fecha de vencimiento de la revisión técnica")
    operation_permit_expiry = models.DateField(null=True, blank=True, help_text="Fecha de vencimiento del permiso de operación")

    def __str__(self):
        return f"{self.license_plate} - {self.brand} {self.model}"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        unique_together = [['company', 'identifier_number'], ['company', 'license_plate'],
                           ['company', 'chassis_number']]