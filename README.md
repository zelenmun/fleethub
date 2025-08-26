# FleetHub - Documentación de Estructura del Proyecto

## Descripción General

FleetHub es una aplicación web multi-tenant tipo ERP para gestión de cooperativas de transporte público en tricimotos. Maneja múltiples empresas através de subdominios y está dirigida a administrativos de dichas compañías.

### Características Principales
- **Multi-tenant**: Cada empresa accede via subdominio (empresa1.fleethub.com)
- **Usuarios objetivo**: Máximo 20 usuarios por empresa
- **Roles**: Director, Gerente General, Secretaria, Tesorero/a (orden jerárquico)
- **Core business**: Gestión de socios propietarios de tricimotos, cobro diario de $1, multas, revisiones semestrales

## Estructura de Carpetas del Proyecto

```
fleethub/
│
├── fleethub/                     # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings/                 # Settings divididos por ambiente
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                         # Todos los módulos/apps
│   ├── __init__.py
│   ├── core/                     # Core del sistema (tenant management, auth, etc.)
│   │   ├── migrations/
│   │   ├── management/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── utils/
│   │   └── permissions/
│   │
│   ├── accounts/                 # Gestión de usuarios y roles
│   ├── inventory/                # Módulo de inventario
│   ├── finance/                  # Módulo financiero
│   ├── reports/                  # Módulo de reportes
│   ├── notifications/            # Sistema de notificaciones
│   └── api/                      # API endpoints centralizados
│
├── shared/                       # Código compartido entre módulos
│   ├── __init__.py
│   ├── mixins/
│   ├── decorators/
│   ├── validators/
│   ├── exceptions/
│   ├── constants/
│   └── utils/
│
├── templates/                    # Templates globales
│   ├── base/
│   ├── emails/
│   └── errors/
│
├── static/                       # Archivos estáticos
│   ├── css/
│   ├── js/
│   ├── images/
│   └── vendors/
│
├── media/                        # Archivos subidos por usuarios
│   └── tenants/                  # Organizados por tenant
│       └── {tenant_id}/
│
├── locale/                       # Archivos de internacionalización
│
├── deployment/                   # Configuraciones de despliegue
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/                         # Documentación
│   ├── api/
│   ├── modules/
│   └── deployment/
│
├── tests/                        # Tests centralizados
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── requirements/                 # Dependencias por ambiente
│   ├── base.txt
│   ├── development.txt
│   ├── staging.txt
│   └── production.txt
│
├── manage.py
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Aplicaciones Django Definidas

### 1. **Core** (Aplicación base)
**Propósito**: Modelos base y funcionalidad común para todas las aplicaciones.

**Modelos principales**:
- `BaseModel`: Modelo abstracto base con auditoría (UUID, timestamps, soft delete)
- `Company`: Empresas del sistema (multi-tenant)
- `TenantBaseModel`: Modelo base para entidades que pertenecen a una empresa
- `Person`: Modelo abstracto para personas del sistema
- `SingleAddressMixin`: Mixin para direcciones únicas

**Responsabilidades**:
- Proporcionar modelos base para herencia
- Gestión multi-tenant
- Middleware para filtrado por subdominio
- Utilidades compartidas

### 2. **Shareholders** (Gestión de socios)
**Propósito**: Gestión de socios propietarios de vehículos y usuarios del sistema.

**Modelos principales**:
- `Partner`: Socios de las cooperativas (hereda de Person)
- `CompanyUser`: Usuarios administrativos del sistema

**Funcionalidades**:
- CRUD de socios
- Gestión de usuarios por rol (Director, Gerente, Secretaria, Tesorero)
- Historial de actividad de socios

### 3. **Fleet** (Gestión de flota)
**Propósito**: Gestión de vehículos y su información.

**Modelos principales**:
- `Vehicle`: Vehículos del sistema
- `VehicleType`: Tipos de vehículos
- `VehicleDocument`: Documentos de vehículos

### 4. **Finance** (Gestión financiera)
**Propósito**: Manejo de cobros, multas y finanzas de la cooperativa.

**Modelos principales**:
- `DailyFee`: Cobros diarios ($1 por día)
- `Fine`: Multas aplicadas
- `Payment`: Pagos realizados
- `Account`: Cuentas financieras

### 5. **Maintenance** (Mantenimiento)
**Propósito**: Gestión de revisiones y mantenimiento de vehículos.

**Modelos principales**:
- `MaintenanceRecord`: Registros de mantenimiento
- `Inspection`: Revisiones semestrales
- `MaintenanceType`: Tipos de mantenimiento

### 6. **Inventory** (Inventario)
**Propósito**: Gestión de inventario y materiales.

**Modelos principales**:
- `Product`: Productos del inventario
- `Stock`: Control de existencias
- `Movement`: Movimientos de inventario

## Dependencias Principales

### Dependencias base (requirements/base.txt)
```
Django>=4.2.0
django-cities-light>=3.9.0
python-decouple>=3.8
Pillow>=10.0.0
django-extensions>=3.2.0
psycopg2-binary>=2.9.0
celery>=5.3.0
redis>=5.0.0
```

### Dependencias de desarrollo (requirements/development.txt)
```
-r base.txt
django-debug-toolbar>=4.2.0
pytest-django>=4.5.0
factory-boy>=3.3.0
black>=23.0.0
flake8>=6.0.0
```

## Orden de Implementación Recomendado

1. **Core**: Establecer modelos base y multi-tenancy
2. **Shareholders**: Gestión de socios y usuarios (depende de Core)
3. **Fleet**: Gestión de vehículos (depende de Shareholders)
4. **Finance**: Cobros y multas (depende de Shareholders y Fleet)
5. **Maintenance**: Revisiones (depende de Fleet)
6. **Inventory**: Gestión de materiales (último en prioridad)

## Configuración Multi-Tenant

### Subdominios
- `empresa1.fleethub.com` → Company ID = 1
- `empresa2.fleethub.com` → Company ID = 2
- `empresa3.fleethub.com` → Company ID = 3

### Middleware Multi-Tenant
El middleware `core.middleware.TenantMiddleware` extrae el subdominio de la URL y establece la empresa actual en el contexto de la request.

### Filtrado Automático
Todos los modelos que heredan de `TenantBaseModel` se filtran automáticamente por la empresa del usuario logueado.

## Roles y Permisos

### Jerarquía de Roles (de mayor a menor autoridad)
1. **Director**: Acceso completo al sistema
2. **Gerente General**: Acceso a todas las operaciones excepto configuración crítica
3. **Secretaria**: Gestión de socios, documentos y comunicaciones
4. **Tesorero/a**: Gestión financiera y cobros

## Notas Técnicas

### Identificadores
- Todos los modelos usan UUID como Primary Key para mejor compatibilidad multi-tenant
- Evita conflictos de ID entre empresas

### Auditoría
- Todos los modelos heredan campos de auditoría (created_at, updated_at, created_by, updated_by)
- Soft delete implementado con campo `is_active`

### Datos Geográficos
- Se utiliza `django-cities-light` para países, provincias y ciudades
- Comando: `python manage.py cities_light` para importar datos de GeoNames

### Base de Datos
- Optimizada para PostgreSQL
- Índices definidos para consultas multi-tenant eficientes