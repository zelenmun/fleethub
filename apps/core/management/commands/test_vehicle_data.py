from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.models import Vehicle
import json
import os


class Command(BaseCommand):
    help = 'Carga datos de prueba para los vehículos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elimina todos los datos existentes antes de cargar',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='vehicle_test_data_json.json',
            help='Nombre del archivo JSON con los datos (por defecto: vehicle_test_data_json.json)',
        )

    def handle(self, *args, **options):
        if options['delete']:
            Vehicle.objects.all().delete()
            self.stdout.write('Datos existentes eliminados.')

        # Cargar datos desde archivo JSON en apps/core/management/commands/test/
        file_path = os.path.join(settings.BASE_DIR, 'apps', 'core', 'management', 'test', options['file'])

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                vehicles_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'❌ Archivo no encontrado: {file_path}')
            )
            return
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al decodificar JSON: {e}')
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {e}')
            )
            return

        if not isinstance(vehicles_data, list):
            self.stdout.write(
                self.style.ERROR('❌ El archivo JSON debe contener una lista de vehículos')
            )
            return

        created_count = 0
        updated_count = 0

        for data in vehicles_data:
            try:
                vehicle, created = Vehicle.objects.get_or_create(
                    identifier_number=data['identifier_number'],
                    defaults=data
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Creado: {vehicle.license_plate} - {vehicle.brand} {vehicle.model}')
                else:
                    updated_count += 1
                    self.stdout.write(f'⚠️  Ya existe: {vehicle.license_plate} - {vehicle.brand} {vehicle.model}')
            except KeyError as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Campo faltante {e} en registro: {data}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creando vehículo {data.get("license_plate", "desconocido")}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. {created_count} vehículos creados, {updated_count} ya existían.'
            )
        )