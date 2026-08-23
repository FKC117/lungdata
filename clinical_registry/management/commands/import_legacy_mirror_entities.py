from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils import timezone

from clinical_registry.models import (
    Center,
    Doctor,
    DoctorDegree,
    DoctorPatient,
    DoctorRecognitionRecord,
    LegacyUser,
    Patient,
)


class Command(BaseCommand):
    help = "Import mirrored doctor and center entities from the legacy MySQL database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete mirrored doctor/center data before importing.",
        )

    def handle(self, *args, **options):
        if options["truncate"]:
            self._truncate_target_data()

        with transaction.atomic():
            self.import_centers()
            self.import_doctors()
            self.import_doctor_degrees()
            self.import_doctor_patients()
            self.import_doctor_recognition_records()
            self.import_legacy_users()

        self.stdout.write(self.style.SUCCESS("Legacy mirror entity import completed successfully."))

    def legacy_rows(self, query):
        with connections["legacy"].cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(columns, row))

    def clean_str(self, value):
        return value or ""

    def clean_timestamp(self, value):
        if value is None:
            return timezone.now()
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def get_center(self, legacy_id):
        return Center.objects.get(legacy_id=legacy_id)

    def get_doctor(self, legacy_id):
        return Doctor.objects.get(legacy_id=legacy_id)

    def get_patient(self, legacy_id):
        return Patient.objects.get(legacy_id=legacy_id)

    def _truncate_target_data(self):
        for model in [DoctorPatient, DoctorDegree, Doctor, DoctorRecognitionRecord, LegacyUser, Center]:
            model.objects.all().delete()
        self.stdout.write(self.style.WARNING("Mirrored doctor/center data truncated."))

    def import_centers(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM centers ORDER BY id"):
            Center.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "name": row["name"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported centers: {count}"))

    def import_doctors(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM doctors ORDER BY id"):
            center = None
            if row["center_id"]:
                center = Center.objects.filter(legacy_id=row["center_id"]).first()
            Doctor.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "name": row["name"],
                    "phone": self.clean_str(row["phone"]),
                    "email": self.clean_str(row["email"]),
                    "date_of_birth": row["date_of_birth"],
                    "designation": self.clean_str(row["designation"]),
                    "department": self.clean_str(row["department"]),
                    "institution": self.clean_str(row["institution"]),
                    "bmdc_number": self.clean_str(row["bmdc_number"]),
                    "photo": self.clean_str(row["photo"]),
                    "center": center,
                    "password": self.clean_str(row["password"]),
                    "status": self.clean_str(row["status"]),
                    "created_at": self.clean_timestamp(row["created_at"]),
                    "updated_at": self.clean_timestamp(row["updated_at"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported doctors: {count}"))

    def import_doctor_degrees(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM doctor_degrees ORDER BY id"):
            doctor = self.get_doctor(row["doctor_id"])
            DoctorDegree.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "doctor": doctor,
                    "degree": row["degree"],
                    "created_at": self.clean_timestamp(row["created_at"]),
                    "updated_at": self.clean_timestamp(row["updated_at"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported doctor_degrees: {count}"))

    def import_doctor_patients(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM doctor_patients ORDER BY id"):
            doctor = self.get_doctor(row["doctor_id"])
            patient = self.get_patient(row["patient_id"])
            DoctorPatient.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "doctor": doctor,
                    "patient": patient,
                    "created_at": self.clean_timestamp(row["created_at"]),
                    "updated_at": self.clean_timestamp(row["updated_at"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported doctor_patients: {count}"))

    def import_doctor_recognition_records(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM doctor_recognition_records ORDER BY id"):
            DoctorRecognitionRecord.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "group": row["group"],
                    "value": row["value"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported doctor_recognition_records: {count}"))

    def import_legacy_users(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM users ORDER BY id"):
            LegacyUser.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                    "email_verified_at": row["email_verified_at"],
                    "password": row["password"],
                    "status": row["status"],
                    "remember_token": self.clean_str(row["remember_token"]),
                    "created_at": self.clean_timestamp(row["created_at"]),
                    "updated_at": self.clean_timestamp(row["updated_at"]),
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported legacy users: {count}"))
