from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Q

from clinical_registry.models import (
    ChemotherapyModality,
    ChemotherapyProtocol,
    ClinicalObservation,
    Patient,
    TreatmentCycle,
)


class Command(BaseCommand):
    help = "Read-only comparison of source and canonical treatment cycles for one patient phone number."

    def add_arguments(self, parser):
        parser.add_argument("phone")
        parser.add_argument("--source-db", default="recent", choices=["legacy", "recent"])

    def handle(self, *args, **options):
        identifier = options["phone"].strip()
        if not identifier:
            raise CommandError("A phone number, HN, or registration number is required.")

        patient = Patient.objects.filter(
            Q(phone=identifier)
            | Q(registration_no=identifier)
            | Q(legacy_unique_id=identifier)
        ).first()
        observations = list(ClinicalObservation.objects.filter(patient=patient)) if patient else []
        canonical_cycles = list(
            TreatmentCycle.objects.filter(observation__in=observations)
            .order_by("observation_id", "id")
            .values_list(
                "observation__legacy_id",
                "legacy_id",
                "current_chemo_protocol",
                "chemo_cycle_no",
                "line_of_treatment",
                "chemo_starting_date",
            )
        )
        canonical_protocols = list(
            ChemotherapyProtocol.objects.filter(treatment_cycle__in=TreatmentCycle.objects.filter(observation__in=observations))
            .order_by("treatment_cycle_id", "id")
            .values_list("treatment_cycle__legacy_id", "legacy_id", "protocol_type", "cycle_no")
        )
        canonical_modalities = list(
            ChemotherapyModality.objects.filter(treatment_cycle__in=TreatmentCycle.objects.filter(observation__in=observations))
            .order_by("treatment_cycle_id", "id")
            .values_list("treatment_cycle__legacy_id", "legacy_id", "detail")
        )

        self.stdout.write(f"Canonical patient: {patient.registry_id if patient else 'not found'}")
        self.stdout.write(f"Canonical observations: {[(item.id, item.legacy_id) for item in observations]}")
        self.stdout.write(f"Canonical cycles: {canonical_cycles}")
        self.stdout.write(f"Canonical protocols: {canonical_protocols}")
        self.stdout.write(f"Canonical modalities: {canonical_modalities}")

        with connections[options["source_db"]].cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.id AS patient_id,
                    p.name,
                    o.id AS observation_id,
                    o.is_draft,
                    d.id AS treatment_detail_id,
                    d.current_chemo_protocol,
                    d.chemo_cycle_no,
                    d.line_of_treatment,
                    d.chemo_starting_date
                FROM patients p
                LEFT JOIN patient_observations o ON o.patient_id = p.id
                LEFT JOIN patient_observation_details d ON d.patient_observation_id = o.id
                WHERE p.phone = %s OR p.unique_id = %s OR o.registration_no = %s
                ORDER BY o.id, d.id
                """,
                [identifier, identifier, identifier],
            )
            source_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    case_id,
                    patient_id,
                    source_observation_ids,
                    last_observation_time,
                    observation_details
                FROM patient_registration_case_full
                WHERE phone = %s
                   OR normalized_registration_no = %s
                   OR registration_numbers LIKE %s
                ORDER BY last_observation_time DESC, case_id DESC
                """,
                [identifier, f"REG:{identifier}", f"%{identifier}%"],
            )
            consolidated_rows = cursor.fetchall()

        self.stdout.write(f"{options['source_db']} rows: {source_rows}")
        self.stdout.write(f"{options['source_db']} consolidated rows: {consolidated_rows}")
