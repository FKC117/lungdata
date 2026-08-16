from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinical_registry.models import Doctor, DoctorProfile


class Command(BaseCommand):
    help = "Explicitly link a DoctorProfile to a mirrored Doctor record."

    def add_arguments(self, parser):
        parser.add_argument("profile_id", type=int, help="DoctorProfile primary key.")
        parser.add_argument("doctor_id", type=int, help="Doctor primary key.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the intended link without saving it.",
        )

    def handle(self, *args, **options):
        profile_id = options["profile_id"]
        doctor_id = options["doctor_id"]
        dry_run = options["dry_run"]

        try:
            profile = DoctorProfile.objects.select_related("user", "doctor").get(pk=profile_id)
        except DoctorProfile.DoesNotExist as exc:
            raise CommandError(f"DoctorProfile #{profile_id} does not exist.") from exc

        try:
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist as exc:
            raise CommandError(f"Doctor #{doctor_id} does not exist.") from exc

        self.stdout.write(
            self.style.NOTICE(
                f"Profile #{profile.pk} ({profile.display_name or profile.user.username}) "
                f"-> Doctor #{doctor.pk} ({doctor.name})"
            )
        )

        if profile.doctor_id == doctor.pk:
            self.stdout.write(self.style.SUCCESS("Profile is already linked to this doctor."))
            return

        if profile.doctor_id:
            self.stdout.write(
                self.style.WARNING(
                    f"Profile currently links to Doctor #{profile.doctor_id} ({profile.doctor.name})."
                )
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No changes were saved."))
            return

        with transaction.atomic():
            profile.doctor = doctor
            profile.save(update_fields=["doctor", "updated_at"])

        self.stdout.write(self.style.SUCCESS("Doctor profile link saved successfully."))
