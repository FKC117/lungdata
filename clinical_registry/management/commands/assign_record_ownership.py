from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinical_registry.models import ClinicalObservation, Patient


class Command(BaseCommand):
    help = "Assign canonical patient and observation ownership to a Django user."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username that should own the selected records.")
        parser.add_argument(
            "--all-unassigned",
            action="store_true",
            help="Assign every patient and observation that has no owner yet.",
        )
        parser.add_argument(
            "--registry-ids",
            nargs="+",
            help="Specific patient registry IDs to assign.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving it.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        all_unassigned = options["all_unassigned"]
        registry_ids = options.get("registry_ids") or []
        dry_run = options["dry_run"]

        if not all_unassigned and not registry_ids:
            raise CommandError("Provide either --all-unassigned or one or more --registry-ids values.")

        user_model = get_user_model()
        try:
            owner = user_model.objects.get(username=username)
        except user_model.DoesNotExist as exc:
            raise CommandError(f"User '{username}' does not exist.") from exc

        patients_qs = Patient.objects.all()
        observations_qs = ClinicalObservation.objects.all()

        if all_unassigned:
            patients_qs = patients_qs.filter(created_by__isnull=True)
            observations_qs = observations_qs.filter(created_by__isnull=True)
        else:
            patients_qs = patients_qs.filter(registry_id__in=registry_ids)
            observations_qs = observations_qs.filter(patient__registry_id__in=registry_ids)

        patient_count = patients_qs.count()
        observation_count = observations_qs.count()

        self.stdout.write(
            self.style.NOTICE(
                f"Target owner: {owner.username} | patients: {patient_count} | observations: {observation_count}"
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No records were updated."))
            return

        with transaction.atomic():
            patients_qs.update(created_by=owner)
            observations_qs.update(created_by=owner)

        self.stdout.write(self.style.SUCCESS("Ownership assignment completed successfully."))
