from django.core.management.base import BaseCommand
from django.db import connection
from fhirapi.models import Doctor

class Command(BaseCommand):
    help = 'Load doctor data from existing PostgreSQL table into Django model'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT practitioner_id, first_name, last_name, specialization, phone, email,
                       address, city, state, zip_code
                FROM doctors
            """)
            rows = cursor.fetchall()

            for row in rows:
                Doctor.objects.update_or_create(
                    practitioner_id=row[0],
                    defaults={
                        'first_name': row[1],
                        'last_name': row[2],
                        'specialization': row[3],
                        'phone': row[4],
                        'email': row[5],
                        'address': row[6],
                        'city': row[7],
                        'state': row[8],
                        'zip_code': row[9],
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"Imported {len(rows)} doctors from external table."))
