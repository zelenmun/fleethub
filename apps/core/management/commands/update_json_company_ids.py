from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.models import Company
import json
import os
import random
import uuid


class Command(BaseCommand):
    help = 'Actualiza archivos JSON agregando company_id aleatorio a registros que lo requieran'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            type=str,
            default='test',
            help='Directorio donde están los archivos JSON (por defecto: test)',
        )
        parser.add_argument(
            '--files',
            nargs='*',
            help='Archivos específicos a procesar (por defecto: todos los .json del directorio)',
        )
        parser.add_argument(
            '--company-fields',
            nargs='*',
            default=['company_id', 'object_id'],
            help='Nombres de campos que deben contener el UUID de compañía (por defecto: company_id, object_id)',
        )

    def handle(self, *args, **options):
        # Obtener todas las compañías existentes
        companies = list(Company.objects.all())

        if not companies:
            self.stdout.write(
                self.style.ERROR('❌ No hay compañías en la base de datos. Ejecuta primero load_companies.')
            )
            return

        company_uuids = [str(company.id) for company in companies]
        company_fields = options['company_fields']

        self.stdout.write(f'📋 Encontradas {len(company_uuids)} compañías disponibles.')
        self.stdout.write(f'🔍 Buscando campos: {", ".join(company_fields)}')

        # Directorio de archivos JSON
        json_directory = os.path.join(
            settings.BASE_DIR,
            'apps',
            'core',
            'management',
            options['directory']
        )

        if not os.path.exists(json_directory):
            self.stdout.write(
                self.style.ERROR(f'❌ Directorio no encontrado: {json_directory}')
            )
            return

        # Determinar archivos a procesar
        if options['files']:
            files_to_process = options['files']
        else:
            files_to_process = [f for f in os.listdir(json_directory) if f.endswith('.json')]

        if not files_to_process:
            self.stdout.write(
                self.style.WARNING('⚠️  No se encontraron archivos JSON para procesar.')
            )
            return

        processed_files = 0
        updated_records = 0

        for filename in files_to_process:
            file_path = os.path.join(json_directory, filename)

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Archivo no encontrado: {filename}')
                )
                continue

            try:
                # Leer archivo JSON
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                if not isinstance(data, list):
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {filename}: No es una lista, saltando.')
                    )
                    continue

                # Verificar si algún registro necesita alguno de los campos de compañía
                needs_company_field = any(
                    isinstance(record, dict) and any(field in record for field in company_fields)
                    for record in data
                )

                if not needs_company_field:
                    self.stdout.write(f'ℹ️  {filename}: No contiene campos de compañía, saltando.')
                    continue

                # Crear un iterador cíclico de UUIDs de compañías
                company_cycle = self._cycle_generator(company_uuids)
                file_updated_records = 0
                fields_found = set()

                # Actualizar registros que tengan alguno de los campos de compañía
                for record in data:
                    if isinstance(record, dict):
                        for field in company_fields:
                            if field in record:
                                # Asignar UUID de compañía de forma cíclica
                                record[field] = next(company_cycle)
                                file_updated_records += 1
                                fields_found.add(field)
                                break  # Solo actualizar el primer campo encontrado por registro

                # Guardar archivo actualizado
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)

                processed_files += 1
                updated_records += file_updated_records
                self.stdout.write(
                    f'✅ {filename}: {file_updated_records} registros actualizados '
                    f'(campos: {", ".join(fields_found)})'
                )

            except json.JSONDecodeError as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error JSON en {filename}: {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error procesando {filename}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Proceso completado. {processed_files} archivos procesados, '
                f'{updated_records} registros actualizados.'
            )
        )

    def _cycle_generator(self, items):
        """Generador que cicla infinitamente a través de una lista de items."""
        shuffled_items = items.copy()
        random.shuffle(shuffled_items)  # Mezclar para mayor aleatoriedad

        while True:
            for item in shuffled_items:
                yield item
            # Volver a mezclar al completar un ciclo
            random.shuffle(shuffled_items)