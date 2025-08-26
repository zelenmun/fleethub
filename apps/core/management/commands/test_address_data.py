from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from apps.core.models import Address
import json
import os


class Command(BaseCommand):
    help = 'Carga datos de prueba para las direcciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elimina todos los datos existentes antes de cargar',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='address_test_data_json.json',
            help='Nombre del archivo JSON con los datos (por defecto: address_test_data_json.json)',
        )

    def handle(self, *args, **options):
        if options['delete']:
            Address.objects.all().delete()
            self.stdout.write('Datos existentes eliminados.')

        # Cargar datos desde archivo JSON en apps/core/management/commands/test/
        file_path = os.path.join(
            settings.BASE_DIR,
            'apps',
            'core',
            'management',
            'test',
            options['file']
        )

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                addresses_data = json.load(file)
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

        if not isinstance(addresses_data, list):
            self.stdout.write(
                self.style.ERROR('❌ El archivo JSON debe contener una lista de direcciones')
            )
            return

        created_count = 0
        updated_count = 0

        for data in addresses_data:
            try:
                # Manejar content_type si viene como string
                content_type_data = data.get('content_type')
                if isinstance(content_type_data, str):
                    # Buscar ContentType por nombre del modelo
                    try:
                        content_type = ContentType.objects.get(model=content_type_data.lower())
                        data['content_type'] = content_type
                    except ContentType.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f'❌ ContentType no encontrado: {content_type_data}')
                        )
                        continue
                elif isinstance(content_type_data, int):
                    # Buscar ContentType por ID
                    try:
                        content_type = ContentType.objects.get(id=content_type_data)
                        data['content_type'] = content_type
                    except ContentType.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f'❌ ContentType con ID {content_type_data} no encontrado')
                        )
                        continue

                # Crear dirección usando combinación de campos como identificador único
                address, created = Address.objects.get_or_create(
                    content_type=data['content_type'],
                    object_id=data['object_id'],
                    city=data['city'],
                    province=data['province'],
                    defaults=data
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        f'✅ Creada: {address.city}, {address.province} '
                        f'({address.content_type.model})'
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        f'⚠️  Ya existe: {address.city}, {address.province} '
                        f'({address.content_type.model})'
                    )

            except KeyError as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Campo faltante {e} en registro: {data}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error creando dirección {data.get("city", "desconocida")}: {e}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. {created_count} direcciones creadas, {updated_count} ya existían.'
            )
        )