# FleetHub API REST Documentation

Esta documentación describe las APIs REST disponibles para el sistema FleetHub, un ERP para empresas de transporte en tricimotos.

## Base URL
```
http://127.0.0.1:8000/api/
```

---

## 1. Companies API

### Descripción
Gestión de compañías en el sistema multi-tenant.

### Endpoints Disponibles

#### **GET** `/api/companies/`
Lista todas las compañías activas.

**Respuesta de ejemplo:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Tricimoto Express",
    "subdomain": "tricimoto-express",
    "legal_name": "Tricimoto Express S.A.",
    "tax_id": "1234567890001",
    "phone": "0987654321",
    "email": "info@tricimoto.com",
    "daily_fee": "1.50",
    "is_active": true,
    "created_at": "2024-08-25T15:30:00Z",
    "updated_at": "2024-08-25T15:30:00Z"
  }
]
```

#### **POST** `/api/companies/`
Crea una nueva compañía.

**Body requerido:**
```json
{
  "name": "Nueva Compañía",
  "subdomain": "nueva-compania",
  "legal_name": "Nueva Compañía S.A.",
  "tax_id": "1234567890008",
  "phone": "0987654321",
  "email": "info@nueva.com",
  "daily_fee": "1.25"
}
```

**Validaciones:**
- `subdomain`: Único, mínimo 3 caracteres, solo letras, números y guiones
- `tax_id`: Único, mínimo 10 dígitos
- `daily_fee`: Valor decimal positivo

#### **GET** `/api/companies/{id}/`
Obtiene una compañía específica.

#### **PUT/PATCH** `/api/companies/{id}/`
Actualiza una compañía existente.

#### **DELETE** `/api/companies/{id}/`
Eliminación física de la compañía.

### Endpoints Personalizados

#### **POST** `/api/companies/{id}/soft_delete/`
Eliminación lógica (desactivación) de la compañía.

#### **POST** `/api/companies/{id}/restore/`
Restaura una compañía desactivada.

#### **GET** `/api/companies/by_subdomain/?subdomain=tricimoto-express`
Busca una compañía por su subdominio.

#### **GET** `/api/companies/{id}/stats/`
Estadísticas básicas de la compañía.

**Respuesta de ejemplo:**
```json
{
  "company_name": "Tricimoto Express",
  "daily_fee": "1.50",
  "created_at": "2024-08-25T15:30:00Z",
  "is_active": true
}
```

---

## 2. Addresses API

### Descripción
Gestión de direcciones polimórficas en el sistema, integrada con Cities Light para datos geográficos.

### Endpoints Disponibles

#### **GET** `/api/addresses/`
Lista todas las direcciones activas.

**Parámetros de filtro opcionales:**
- `content_type`: Filtrar por tipo de objeto (ej: `company`)
- `object_id`: Filtrar por ID de objeto específico
- `city`: Filtrar por ciudad (búsqueda parcial)

**Respuesta de ejemplo:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "full_address": "Las Peñas, Guayaquil, Guayas, Ecuador",
    "related_object": {
      "type": "company",
      "name": "Tricimoto Express"
    },
    "created_at": "2024-08-25T15:30:00Z"
  }
]
```

#### **POST** `/api/addresses/`
Crea una nueva dirección.

**Body requerido:**
```json
{
  "country": "Ecuador",
  "province": "Guayas",
  "city": "Guayaquil",
  "sector": "Las Peñas",
  "postal_code": "090313",
  "reference": "Frente al Malecón 2000, edificio azul",
  "content_type": 1,
  "object_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Validaciones:**
- `city` y `province` son obligatorios
- Formato de texto se normaliza (Title Case)

#### **GET** `/api/addresses/{id}/`
Obtiene una dirección específica con información completa.

**Respuesta de ejemplo:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "country": "Ecuador",
  "province": "Guayas",
  "city": "Guayaquil",
  "sector": "Las Peñas",
  "postal_code": "090313",
  "reference": "Frente al Malecón 2000, edificio azul",
  "content_type": 1,
  "object_id": "123e4567-e89b-12d3-a456-426614174000",
  "full_address": "Las Peñas, Guayaquil, Guayas, Ecuador",
  "created_at": "2024-08-25T15:30:00Z",
  "updated_at": "2024-08-25T15:30:00Z",
  "is_active": true
}
```

#### **PUT/PATCH** `/api/addresses/{id}/`
Actualiza una dirección existente.

#### **DELETE** `/api/addresses/{id}/`
Eliminación física de la dirección.

### Endpoints Personalizados

#### **POST** `/api/addresses/{id}/soft_delete/`
Eliminación lógica de la dirección.

#### **POST** `/api/addresses/{id}/restore/`
Restaura una dirección desactivada.

### Endpoints para Selects (Cities Light)

#### **GET** `/api/addresses/countries/`
Lista de países disponibles.

**Respuesta de ejemplo:**
```json
[
  {
    "id": 1,
    "name": "Ecuador",
    "code": "EC"
  },
  {
    "id": 2,
    "name": "Colombia",
    "code": "CO"
  }
]
```

#### **GET** `/api/addresses/regions/?country_id=1`
Lista de provincias filtradas por país.

**Respuesta de ejemplo:**
```json
[
  {
    "id": 1,
    "name": "Guayas"
  },
  {
    "id": 2,
    "name": "Pichincha"
  }
]
```

#### **GET** `/api/addresses/cities/?region_id=1`
Lista de ciudades filtradas por provincia.

**Respuesta de ejemplo:**
```json
[
  {
    "id": 1,
    "name": "Guayaquil"
  },
  {
    "id": 2,
    "name": "Milagro"
  }
]
```

---

## 3. Vehicles API

### Descripción
Gestión completa de vehículos (tricimotos) con control de estados, documentación y alertas de vencimiento.

### Endpoints Disponibles

#### **GET** `/api/vehicles/`
Lista todos los vehículos activos (vista simplificada).

**Parámetros de filtro opcionales:**
- `company`: UUID de la compañía
- `status`: Estado del vehículo (`active`, `suspended`, `revoked`)
- `license_plate`: Búsqueda parcial por placa
- `brand`: Búsqueda parcial por marca
- `year`: Año específico
- `expiring_soon`: `true` para vehículos con documentos próximos a vencer

**Respuesta de ejemplo:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174002",
    "license_plate": "ABC-1234",
    "vehicle_info": "Toyota Hilux (2020)",
    "status": "active",
    "status_display": "Activo",
    "alert_status": ["SOAT próximo a vencer"],
    "created_at": "2024-08-25T15:30:00Z"
  }
]
```

#### **POST** `/api/vehicles/`
Crea un nuevo vehículo.

**Body requerido:**
```json
{
  "company": "123e4567-e89b-12d3-a456-426614174000",
  "identifier_number": "TRIC-001",
  "license_plate": "ABC-1234",
  "chassis_number": "CH123456789",
  "engine_number": "ENG123456",
  "brand": "Bajaj",
  "model": "RE Compact",
  "year": 2022,
  "color": "Amarillo",
  "engine_displacement": 200,
  "passenger_capacity": 3,
  "soat_expiry": "2025-12-31",
  "technical_review_expiry": "2025-06-30",
  "operation_permit_expiry": "2025-12-31"
}
```

**Validaciones:**
- `license_plate`: Formato ecuatoriano ABC-1234
- `year`: Entre 1990 y año actual + 1
- `engine_displacement`: Entre 50cc y 500cc
- `passenger_capacity`: Entre 1 y 6 pasajeros
- Unicidad por compañía: placa, chasis, número identificador

#### **GET** `/api/vehicles/{id}/`
Obtiene un vehículo específico con información completa.

**Respuesta de ejemplo:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "company": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "Tricimoto Express",
  "identifier_number": "TRIC-001",
  "license_plate": "ABC-1234",
  "chassis_number": "CH123456789",
  "engine_number": "ENG123456",
  "brand": "Bajaj",
  "model": "RE Compact",
  "year": 2022,
  "color": "Amarillo",
  "engine_displacement": 200,
  "passenger_capacity": 3,
  "status": "active",
  "status_display": "Activo",
  "status_changed_at": "2024-08-25T15:30:00Z",
  "soat_expiry": "2025-12-31",
  "technical_review_expiry": "2025-06-30",
  "operation_permit_expiry": "2025-12-31",
  "days_until_soat_expiry": 127,
  "days_until_technical_review_expiry": -58,
  "days_until_operation_permit_expiry": 127,
  "vehicle_age": 2,
  "is_active": true,
  "created_at": "2024-08-25T15:30:00Z",
  "updated_at": "2024-08-25T15:30:00Z"
}
```

#### **PUT/PATCH** `/api/vehicles/{id}/`
Actualiza un vehículo existente.

#### **DELETE** `/api/vehicles/{id}/`
Eliminación física del vehículo.

### Endpoints Personalizados

#### **POST** `/api/vehicles/{id}/soft_delete/`
Eliminación lógica del vehículo.

#### **POST** `/api/vehicles/{id}/restore/`
Restaura un vehículo desactivado.

#### **PATCH** `/api/vehicles/{id}/update_status/`
Actualiza el estado del vehículo con control de transiciones.

**Body requerido:**
```json
{
  "status": "suspended",
  "reason": "Mantenimiento programado"
}
```

**Transiciones permitidas:**
- `active` → `suspended`, `revoked`
- `suspended` → `active`, `revoked`
- `revoked` → (sin cambios permitidos)

#### **GET** `/api/vehicles/search/?q=ABC123`
Búsqueda avanzada en múltiples campos.

**Campos de búsqueda:**
- Placa
- Número de chasis
- Número identificador
- Marca
- Modelo
- Número de motor

**Respuesta de ejemplo:**
```json
{
  "query": "ABC123",
  "count": 2,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "license_plate": "ABC-1234",
      "vehicle_info": "Bajaj RE Compact (2022)",
      "status": "active",
      "status_display": "Activo",
      "alert_status": [],
      "created_at": "2024-08-25T15:30:00Z"
    }
  ]
}
```

#### **GET** `/api/vehicles/expiring_documents/?days=30`
Vehículos con documentos próximos a vencer.

**Parámetros:**
- `days`: Días de anticipación para la alerta (default: 30)

**Respuesta de ejemplo:**
```json
{
  "alert_days": 30,
  "expired_count": 2,
  "expiring_count": 3,
  "expired_vehicles": [...],
  "expiring_vehicles": [...]
}
```

#### **GET** `/api/vehicles/stats/`
Estadísticas generales de vehículos.

**Respuesta de ejemplo:**
```json
{
  "total_vehicles": 25,
  "status_breakdown": {
    "active": 20,
    "suspended": 3,
    "revoked": 2
  },
  "top_brands": [
    {"brand": "Bajaj", "count": 15},
    {"brand": "TVS", "count": 8},
    {"brand": "Piaggio", "count": 2}
  ],
  "by_year": [
    {"year": 2023, "count": 10},
    {"year": 2022, "count": 8},
    {"year": 2021, "count": 7}
  ],
  "expired_documents": {
    "soat": 3,
    "technical_review": 5,
    "operation_permits": 2
  }
}
```

#### **GET** `/api/vehicles/{id}/full_details/`
Información completa del vehículo con alertas detalladas.

**Respuesta de ejemplo:**
```json
{
  // ... datos completos del vehículo
  "alerts": [
    {
      "type": "warning",
      "message": "SOAT vence en 15 días"
    },
    {
      "type": "error",
      "message": "Revisión técnica vencida"
    }
  ]
}
```

---

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en los datos enviados
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error interno del servidor

## Paginación

Las listas utilizan paginación automática con 20 elementos por página. La respuesta incluye:
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/vehicles/?page=2",
  "previous": null,
  "results": [...]
}
```

## Notas Importantes

1. **Multi-tenancy**: Todos los modelos excepto `Company` están ligados a una compañía específica
2. **Soft Delete**: Todos los modelos soportan eliminación lógica mediante el campo `is_active`
3. **Auditoría**: Todos los registros incluyen campos de auditoría: `created_at`, `updated_at`, `created_by`, `updated_by`
4. **UUIDs**: Todos los modelos usan UUIDs como clave primaria para mejor seguridad
5. **Validaciones**: Cada API incluye validaciones específicas del dominio del negocio