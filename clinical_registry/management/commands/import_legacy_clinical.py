from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.utils import timezone

from clinical_registry.models import (
    CancerMarker,
    Center,
    ChemotherapyModality,
    ChemotherapyProtocol,
    ChemotherapyProtocolDetail,
    ClinicalObservation,
    ClinicalStaging,
    Comorbidity,
    CovidHistory,
    Diagnosis,
    DiagnosisMetastaticSite,
    Doctor,
    Histopathology,
    IHCDetail,
    Immunohistochemistry,
    MolecularPathology,
    PastTreatmentHistory,
    PathologicalStaging,
    PathologicalStagingDetail,
    Patient,
    PatientHistory,
    LegacyImportAnomaly,
    RadiotherapySchedule,
    RadiotherapyScheduleModality,
    RadiotherapyScheduleSite,
    SmokingHistory,
    Surgery,
    SurgicalLaterality,
    TreatmentCycle,
    TreatmentCycleProgressionSite,
    TuberculosisHistory,
)


class Command(BaseCommand):
    help = "Import clinical data from the legacy MySQL database into the canonical schema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete canonical clinical data before importing.",
        )
        parser.add_argument(
            "--orphan-mode",
            choices=["skip", "audit"],
            default="skip",
            help="How to handle legacy child rows whose parent observation/history/protocol does not exist.",
        )
        parser.add_argument(
            "--source-db",
            choices=["legacy", "recent"],
            default="legacy",
            help="Configured source database alias to import from.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the full import inside a transaction, then roll it back.",
        )

    def handle(self, *args, **options):
        self.skipped_counts = {}
        self.orphan_mode = options["orphan_mode"]
        self.source_database = options["source_db"]
        self.dry_run = options["dry_run"]

        if self.dry_run and options["truncate"]:
            raise CommandError("--dry-run cannot be combined with --truncate.")

        if options["truncate"]:
            self._truncate_target_data()

        if self.orphan_mode == "audit":
            self.audit_orphan_chains()
            self.print_skip_summary()
            self.stdout.write(self.style.SUCCESS("Legacy orphan audit completed successfully."))
            return

        with transaction.atomic():
            self.report_duplicate_legacy_unique_ids()
            self.import_patients()
            self.import_observations()
            self.import_histories()
            self.import_history_children()
            self.import_diagnosis_related()
            self.import_pathology_related()
            self.import_staging_related()
            self.import_treatment_related()
            if self.dry_run:
                transaction.set_rollback(True)

        self.print_skip_summary()
        if self.dry_run:
            self.stdout.write(self.style.WARNING("Clinical import dry-run completed; all changes were rolled back."))
        else:
            self.stdout.write(self.style.SUCCESS("Legacy clinical import completed successfully."))

    def audit_orphan_chains(self):
        self.report_duplicate_legacy_unique_ids()
        self.audit_missing_parent(
            "patient_histories",
            "patient_observation_id",
            set(ClinicalObservation.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "smoking_histories",
            "patient_history_id",
            set(PatientHistory.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "tb_histories",
            "patient_history_id",
            set(PatientHistory.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "covid_histories",
            "patient_history_id",
            set(PatientHistory.objects.values_list("legacy_id", flat=True)),
        )
        for table_name in [
            "diagnoses",
            "diagnosis_metastatic_sites",
            "comorbidities",
            "histopathologies",
            "molecular_pathologies",
            "cancer_markers",
            "ihcs",
            "staging_clinicals",
            "staging_pathologicals",
            "staging_pathological_details",
            "patient_observation_details",
            "past_treatment_histories",
            "radiotherapy_schedules",
            "surgeries",
        ]:
            self.audit_missing_parent(
                table_name,
                "patient_observation_id",
                set(ClinicalObservation.objects.values_list("legacy_id", flat=True)),
            )
        self.audit_missing_parent(
            "ihc_details",
            "ihc_id",
            set(Immunohistochemistry.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "patient_observation_response_rate_progression_sites",
            "patient_observation_detail_id",
            set(TreatmentCycle.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "chemotherapy_protocols",
            "patient_observation_detail_id",
            set(TreatmentCycle.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "chemotherapy_modalities",
            "patient_observation_detail_id",
            set(TreatmentCycle.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "chemotherapy_protocol_details",
            "chemotherapy_protocol_id",
            set(ChemotherapyProtocol.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "radiotherapy_schedule_sites",
            "radiotherapy_schedule_id",
            set(RadiotherapySchedule.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "radiotherapy_schedule_modalities",
            "radiotherapy_schedule_id",
            set(RadiotherapySchedule.objects.values_list("legacy_id", flat=True)),
        )
        self.audit_missing_parent(
            "surgical_lateralities",
            "surgery_id",
            set(Surgery.objects.values_list("legacy_id", flat=True)),
        )

    def audit_missing_parent(self, table_name, reference_field, existing_ids):
        count = 0
        for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
            reference_id = row.get(reference_field)
            if reference_id in existing_ids:
                continue
            self.record_orphan_row(
                table_name,
                row,
                reference_field,
                f"missing {reference_field} {reference_id}",
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Audited {table_name}: {count} unresolved rows"))

    def legacy_rows(self, query):
        with connections[self.source_database].cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(columns, row))

    def bool_value(self, value):
        if value in (None, "", 0, "0"):
            return False
        return bool(value)

    def clean_str(self, value):
        return value or ""

    def normalize_marital_status(self, value):
        cleaned = self.clean_str(value).strip()
        if cleaned.lower() == "vegetarin":
            return ""
        return cleaned

    def normalize_smoking_status(self, value):
        cleaned = self.clean_str(value).strip()
        if cleaned.lower() == "yes":
            return "Smoker"
        return cleaned

    def clean_decimal(self, value):
        if value in (None, ""):
            return None
        return Decimal(str(value))

    def clean_int(self, value):
        if value in (None, ""):
            return None
        return int(value)

    def clean_datetime(self, value):
        if value in (None, ""):
            return None
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def build_registry_id(self, legacy_id):
        return f"REG-{legacy_id:09d}"

    def report_duplicate_legacy_unique_ids(self):
        rows = list(self.legacy_rows("""
            SELECT unique_id, COUNT(*) AS duplicate_count
            FROM patients
            WHERE unique_id IS NOT NULL AND unique_id <> ''
            GROUP BY unique_id
            HAVING duplicate_count > 1
            ORDER BY duplicate_count DESC, unique_id
        """))
        if not rows:
            self.stdout.write(self.style.SUCCESS("No duplicate legacy unique IDs found."))
            return

        self.stdout.write(self.style.WARNING("Duplicate legacy unique IDs detected in source data:"))
        for row in rows:
            self.stdout.write(self.style.WARNING(f"  {row['unique_id']} -> {row['duplicate_count']} rows"))

    def get_patient(self, legacy_id):
        return Patient.objects.get(legacy_id=legacy_id)

    def get_observation(self, legacy_id):
        return ClinicalObservation.objects.get(legacy_id=legacy_id)

    def get_history(self, legacy_id):
        return PatientHistory.objects.get(legacy_id=legacy_id)

    def get_cycle(self, legacy_id):
        return TreatmentCycle.objects.get(legacy_id=legacy_id)

    def get_protocol(self, legacy_id):
        return ChemotherapyProtocol.objects.get(legacy_id=legacy_id)

    def get_ihc(self, legacy_id):
        return Immunohistochemistry.objects.get(legacy_id=legacy_id)

    def get_radiotherapy(self, legacy_id):
        return RadiotherapySchedule.objects.get(legacy_id=legacy_id)

    def get_surgery(self, legacy_id):
        return Surgery.objects.get(legacy_id=legacy_id)

    def skip_row(self, bucket, row_id, reason):
        self.skipped_counts.setdefault(bucket, []).append((row_id, reason))

    def record_orphan_row(self, bucket, row, key_name, reason):
        self.skip_row(bucket, row["id"], reason)
        if self.orphan_mode != "audit":
            return
        LegacyImportAnomaly.objects.update_or_create(
            source_table=bucket,
            legacy_row_id=row["id"],
            missing_reference_field=key_name,
            defaults={
                "missing_reference_id": row.get(key_name),
                "reason": reason,
                "payload": {key: self.serialize_payload_value(value) for key, value in row.items()},
            },
        )

    def serialize_payload_value(self, value):
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        return value

    def print_skip_summary(self):
        if not self.skipped_counts:
            self.stdout.write(self.style.SUCCESS("No orphaned legacy rows were skipped."))
            return

        self.stdout.write(self.style.WARNING("Skipped orphaned legacy rows summary:"))
        for bucket, items in self.skipped_counts.items():
            self.stdout.write(self.style.WARNING(f"  {bucket}: {len(items)} skipped"))
            preview = items[:10]
            for row_id, reason in preview:
                self.stdout.write(self.style.WARNING(f"    row {row_id}: {reason}"))
            if len(items) > len(preview):
                self.stdout.write(self.style.WARNING(f"    ... {len(items) - len(preview)} more"))
        if self.orphan_mode == "audit":
            self.stdout.write(
                self.style.SUCCESS(
                    f"Orphan audit rows stored: {LegacyImportAnomaly.objects.count()}"
                )
            )

    def _truncate_target_data(self):
        for model in [
            SurgicalLaterality,
            Surgery,
            RadiotherapyScheduleModality,
            RadiotherapyScheduleSite,
            RadiotherapySchedule,
            PastTreatmentHistory,
            ChemotherapyModality,
            ChemotherapyProtocolDetail,
            ChemotherapyProtocol,
            TreatmentCycleProgressionSite,
            TreatmentCycle,
            IHCDetail,
            Immunohistochemistry,
            PathologicalStagingDetail,
            PathologicalStaging,
            ClinicalStaging,
            CancerMarker,
            MolecularPathology,
            Histopathology,
            Comorbidity,
            DiagnosisMetastaticSite,
            Diagnosis,
            CovidHistory,
            TuberculosisHistory,
            SmokingHistory,
            PatientHistory,
            ClinicalObservation,
            Patient,
        ]:
            model.objects.all().delete()
        self.stdout.write(self.style.WARNING("Canonical clinical data truncated."))

    def import_patients(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM patients ORDER BY id"):
            Patient.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "registry_id": self.build_registry_id(row["id"]),
                    "legacy_unique_id": self.clean_str(row["unique_id"]),
                    "registration_no": "",
                    "name": row["name"],
                    "phone": self.clean_str(row["phone"]),
                    "email": self.clean_str(row["email"]),
                    "nid": self.clean_str(row["nid"]),
                    "date_of_birth": row["date_of_birth"],
                    "age": row["age"],
                    "gender": self.clean_str(row["gender"]),
                    "blood_group": self.clean_str(row["blood_group"]),
                    "area": self.clean_str(row["area"]),
                    "police_station": self.clean_str(row["police_station"]),
                    "district": self.clean_str(row["district"]),
                    "socio_economic_status": self.clean_str(row["socio_economic_status"]),
                    "photo": self.clean_str(row["photo"]),
                    "passport": self.clean_str(row["passport"]),
                    "patient_type": self.clean_str(row["type"]),
                    "is_draft": self.bool_value(row["is_draft"]),
                    "deleted_at": row["deleted_at"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported patients: {count}"))

    def import_observations(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM patient_observations ORDER BY id"):
            patient = self.get_patient(row["patient_id"])
            doctor = Doctor.objects.filter(legacy_id=row["doctor_id"]).first() if row.get("doctor_id") else None
            center = Center.objects.filter(legacy_id=row["center_id"]).first() if row.get("center_id") else None
            observation, _ = ClinicalObservation.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "patient": patient,
                    "doctor": doctor,
                    "center": center,
                    "time": self.clean_datetime(row["time"]),
                    "observed_at": self.clean_datetime(row["time"]),
                    "registration_no": self.clean_str(row["registration_no"]),
                    "consulting_doctor_name": doctor.name if doctor else "",
                    "center_name": center.name if center else "",
                    "cancer_type": self.clean_str(row["cancer_type"]),
                    "diagnosis_disease_group": self.clean_str(row["diagnosis_disease_group"]),
                    "diagnosis_subgroup": self.clean_str(row["diagnosis_subgroup"]),
                    "diagnosis_primary_site": self.clean_str(row["diagnosis_primary_site"]),
                    "diagnosis_laterility": self.clean_str(row["diagnosis_laterility"]),
                    "diagnosis_laterality": self.clean_str(row["diagnosis_laterility"]),
                    "grade": self.clean_str(row["grade"]),
                    "laterality": self.clean_str(row["laterality"]),
                    "laterality_notes": self.clean_str(row["laterality"]),
                    "is_draft": self.bool_value(row["is_draft"]),
                },
            )
            if not patient.registration_no and observation.registration_no:
                patient.registration_no = observation.registration_no
                patient.save(update_fields=["registration_no"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported observations: {count}"))

    def import_histories(self):
        count = 0
        for row in self.legacy_rows("SELECT * FROM patient_histories ORDER BY id"):
            try:
                observation = self.get_observation(row["patient_observation_id"])
            except ClinicalObservation.DoesNotExist:
                self.record_orphan_row(
                    "patient_histories",
                    row,
                    "patient_observation_id",
                    f"missing patient_observation_id {row['patient_observation_id']}",
                )
                continue
            PatientHistory.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "observation": observation,
                    "marital_status": self.normalize_marital_status(row["marital_status"]),
                    "dietary_habit": self.clean_str(row["dietary_habit"]),
                    "height": self.clean_decimal(row["height"]),
                    "height_cm": self.clean_decimal(row["height"]),
                    "weight": self.clean_decimal(row["weight"]),
                    "weight_kg": self.clean_decimal(row["weight"]),
                    "bmi": self.clean_decimal(row["bmi"]),
                    "h_o_alcoholism": self.clean_str(row["h_o_alcoholism"]),
                    "alcohol_history": self.clean_str(row["h_o_alcoholism"]),
                    "rt_to_chest": self.clean_str(row["rt_to_chest"]),
                    "radiotherapy_to_chest": self.clean_str(row["rt_to_chest"]),
                    "cancer_history": self.clean_str(row["cancer_history"]),
                    "family_cancer_history": self.clean_str(row["cancer_history"]),
                    "known_mutation": self.clean_str(row["known_mutation"]),
                    "first_diagnosis_date": row["first_diagnosis_date"],
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported patient histories: {count}"))

    def import_history_children(self):
        mapping = [
            (
                "smoking_histories",
                SmokingHistory,
                lambda row: {
                    "patient_history": self.get_history(row["patient_history_id"]),
                    "status": self.normalize_smoking_status(row["status"]),
                    "per_day": row["per_day"],
                    "cigarettes_per_day": row["per_day"],
                    "duration_in_year": self.clean_decimal(row["duration_in_year"]),
                    "duration_years": self.clean_decimal(row["duration_in_year"]),
                    "packs_per_year": self.clean_decimal(row["packs_per_year"]),
                    "pack_years": self.clean_decimal(row["packs_per_year"]),
                    "quit_period": self.clean_decimal(row["quit_period"]),
                    "quit_period_years": self.clean_decimal(row["quit_period"]),
                },
            ),
            (
                "tb_histories",
                TuberculosisHistory,
                lambda row: {
                    "patient_history": self.get_history(row["patient_history_id"]),
                    "status": row["status"],
                    "date": row["date"],
                    "treatment": self.clean_str(row["treatment"]),
                },
            ),
            (
                "covid_histories",
                CovidHistory,
                lambda row: {
                    "patient_history": self.get_history(row["patient_history_id"]),
                    "status": row["status"],
                    "date": row["date"],
                    "vaccine_name": self.clean_str(row["vaccine_name"]),
                    "vaccination_dose": self.clean_str(row["vaccination_dose"]),
                },
            ),
        ]
        for table_name, model, builder in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except PatientHistory.DoesNotExist:
                    self.record_orphan_row(
                        table_name,
                        row,
                        "patient_history_id",
                        f"missing patient_history_id {row['patient_history_id']}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

    def import_diagnosis_related(self):
        mapping = [
            (
                "diagnoses",
                Diagnosis,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "detail": self.clean_str(row["detail"]),
                },
            ),
            (
                "diagnosis_metastatic_sites",
                DiagnosisMetastaticSite,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "value": self.clean_str(row["value"]),
                },
            ),
            (
                "comorbidities",
                Comorbidity,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "detail": self.clean_str(row["detail"]),
                },
            ),
        ]
        for table_name, model, builder in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except ClinicalObservation.DoesNotExist:
                    self.record_orphan_row(
                        table_name,
                        row,
                        "patient_observation_id",
                        f"missing patient_observation_id {row['patient_observation_id']}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

    def import_pathology_related(self):
        mapping = [
            (
                "histopathologies",
                Histopathology,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "detail": self.clean_str(row["detail"]),
                    "site": self.clean_str(row["site"]),
                    "histology_type": self.clean_str(row["type"]),
                    "observed_on": row["date"],
                },
            ),
            (
                "molecular_pathologies",
                MolecularPathology,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "specimen": self.clean_str(row["specimen"]),
                    "method": self.clean_str(row["method"]),
                    "gene": self.clean_str(row["gene"]),
                    "exon": self.clean_str(row["exon"]),
                    "status": self.clean_str(row["status"]),
                    "observed_on": row["date"],
                },
            ),
            (
                "cancer_markers",
                CancerMarker,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "name": row["name"],
                    "value": row["value"],
                    "unit": row["unit"],
                    "observed_on": row["date"],
                },
            ),
            (
                "ihcs",
                Immunohistochemistry,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "date": row["date"],
                    "observed_on": row["date"],
                },
            ),
        ]
        for table_name, model, builder in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except ClinicalObservation.DoesNotExist:
                    self.record_orphan_row(
                        table_name,
                        row,
                        "patient_observation_id",
                        f"missing patient_observation_id {row['patient_observation_id']}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

        detail_count = 0
        for row in self.legacy_rows("SELECT * FROM ihc_details ORDER BY id"):
            try:
                ihc = self.get_ihc(row["ihc_id"])
            except Immunohistochemistry.DoesNotExist:
                self.record_orphan_row(
                    "ihc_details",
                    row,
                    "ihc_id",
                    f"missing ihc_id {row['ihc_id']}",
                )
                continue
            IHCDetail.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "ihc": ihc,
                    "type": row["type"],
                    "marker_type": row["type"],
                    "value": self.clean_str(row["value"]),
                },
            )
            detail_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported ihc_details: {detail_count}"))

    def import_staging_related(self):
        mapping = [
            (
                "staging_clinicals",
                ClinicalStaging,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "t": self.clean_str(row["t"]),
                    "n": self.clean_str(row["n"]),
                    "m": self.clean_str(row["m"]),
                    "result": self.clean_str(row["result"]),
                    "date": row["date"],
                    "staged_on": row["date"],
                },
            ),
            (
                "staging_pathologicals",
                PathologicalStaging,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "t": self.clean_str(row["t"]),
                    "n": self.clean_str(row["n"]),
                    "m": self.clean_str(row["m"]),
                    "result": self.clean_str(row["result"]),
                    "date": row["date"],
                    "staged_on": row["date"],
                },
            ),
            (
                "staging_pathological_details",
                PathologicalStagingDetail,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "lvsi": self.clean_str(row["lvsi"]),
                    "pni": self.clean_str(row["pni"]),
                    "margin": self.clean_str(row["margin"]),
                    "ki67": self.clean_str(row["ki67"]),
                    "date": row["date"],
                    "staged_on": row["date"],
                },
            ),
        ]
        for table_name, model, builder in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except ClinicalObservation.DoesNotExist:
                    self.record_orphan_row(
                        table_name,
                        row,
                        "patient_observation_id",
                        f"missing patient_observation_id {row['patient_observation_id']}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

    def import_treatment_related(self):
        cycle_count = 0
        for row in self.legacy_rows("SELECT * FROM patient_observation_details ORDER BY id"):
            try:
                observation = self.get_observation(row["patient_observation_id"])
            except ClinicalObservation.DoesNotExist:
                self.record_orphan_row(
                    "patient_observation_details",
                    row,
                    "patient_observation_id",
                    f"missing patient_observation_id {row['patient_observation_id']}",
                )
                continue
            TreatmentCycle.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "observation": observation,
                    "current_chemo_protocol": self.clean_str(row["current_chemo_protocol"]),
                    "chemo_cycle_no": self.clean_str(row["chemo_cycle_no"]),
                    "chemo_detail": self.clean_str(row["chemo_detail"]),
                    "chemo_starting_date": row["chemo_starting_date"],
                    "chemo_end_date": row["chemo_end_date"],
                    "line_of_treatment": self.clean_str(row["line_of_treatment"]),
                    "disease_progression_status": self.clean_str(row["disease_progression_status"]),
                    "disease_progression_status_date": row["disease_progression_status_date"],
                    "survival_status": self.clean_str(row["survival_status"]),
                    "survival_status_date": row["survival_status_date"],
                    "recist_1_target_lasion": self.clean_str(row["recist_1_target_lasion"]),
                    "recist_1_target_lesion": self.clean_str(row["recist_1_target_lasion"]),
                    "recist_1_non_target_lasion": self.clean_str(row["recist_1_non_target_lasion"]),
                    "recist_1_non_target_lesion": self.clean_str(row["recist_1_non_target_lasion"]),
                    "recist_1_new_lasion": self.clean_str(row["recist_1_new_lasion"]),
                    "recist_1_new_lesion": self.clean_str(row["recist_1_new_lasion"]),
                    "recist_1_result": self.clean_str(row["recist_1_result"]),
                    "recist_1_date": row["recist_1_date"],
                    "recist_1_method_of_estimation": self.clean_str(row["recist_1_method_of_estimation"]),
                    "irecist_target_lasion": self.clean_str(row["irecist_target_lasion"]),
                    "irecist_target_lesion": self.clean_str(row["irecist_target_lasion"]),
                    "irecist_non_target_lasion": self.clean_str(row["irecist_non_target_lasion"]),
                    "irecist_non_target_lesion": self.clean_str(row["irecist_non_target_lasion"]),
                    "irecist_new_lasion": self.clean_str(row["irecist_new_lasion"]),
                    "irecist_new_lesion": self.clean_str(row["irecist_new_lasion"]),
                    "irecist_result": self.clean_str(row["irecist_result"]),
                    "irecist_date": row["irecist_date"],
                    "irecist_method_of_estimation": self.clean_str(row["irecist_method_of_estimation"]),
                    "pathological_response_rate_target_lasion": self.clean_str(
                        row["pathological_response_rate_target_lasion"]
                    ),
                    "pathological_response_rate_target_lesion": self.clean_str(
                        row["pathological_response_rate_target_lasion"]
                    ),
                    "pathological_response_rate_non_target_lasion": self.clean_str(
                        row["pathological_response_rate_non_target_lasion"]
                    ),
                    "pathological_response_rate_non_target_lesion": self.clean_str(
                        row["pathological_response_rate_non_target_lasion"]
                    ),
                    "pathological_response_rate_new_lasion": self.clean_str(
                        row["pathological_response_rate_new_lasion"]
                    ),
                    "pathological_response_rate_new_lesion": self.clean_str(
                        row["pathological_response_rate_new_lasion"]
                    ),
                    "pathological_response_rate_result": self.clean_str(
                        row["pathological_response_rate_result"]
                    ),
                    "pathological_response_rate_date": row["pathological_response_rate_date"],
                    "pathological_method_of_estimation": self.clean_str(row["pathological_method_of_estimation"]),
                    "pfs": self.clean_str(row["pfs"]),
                    "progression_free_survival": self.clean_str(row["pfs"]),
                    "overall_survival": self.clean_str(row["overall_survival"]),
                },
            )
            cycle_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported patient_observation_details: {cycle_count}"))

        child_mapping = [
            (
                "patient_observation_response_rate_progression_sites",
                TreatmentCycleProgressionSite,
                lambda row: {
                    "treatment_cycle": self.get_cycle(row["patient_observation_detail_id"]),
                    "type": row["type"],
                    "site_type": row["type"],
                    "value": row["value"],
                },
            ),
            (
                "chemotherapy_protocols",
                ChemotherapyProtocol,
                lambda row: {
                    "treatment_cycle": self.get_cycle(row["patient_observation_detail_id"]),
                    "cycle_no": self.clean_decimal(row["cycle_no"]),
                    "type": row["type"],
                    "protocol_type": row["type"],
                },
            ),
            (
                "chemotherapy_modalities",
                ChemotherapyModality,
                lambda row: {
                    "treatment_cycle": self.get_cycle(row["patient_observation_detail_id"]),
                    "detail": row["detail"],
                },
            ),
            (
                "past_treatment_histories",
                PastTreatmentHistory,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "detail": self.clean_str(row["detail"]),
                    "date": row["date"],
                },
            ),
            (
                "radiotherapy_schedules",
                RadiotherapySchedule,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "intent": self.clean_str(row["intent"]),
                    "fraction": self.clean_str(row["fraction"]),
                    "fraction_number": self.clean_str(row["fraction_number"]),
                    "total_dose": self.clean_str(row["total_dose"]),
                },
            ),
            (
                "surgeries",
                Surgery,
                lambda row: {
                    "observation": self.get_observation(row["patient_observation_id"]),
                    "surgery_date": row["surgery_date"],
                    "modality": self.clean_str(row["modality"]),
                },
            ),
        ]
        for table_name, model, builder in child_mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except (TreatmentCycle.DoesNotExist, ClinicalObservation.DoesNotExist):
                    key_name = (
                        "patient_observation_detail_id"
                        if "patient_observation_detail_id" in row
                        else "patient_observation_id"
                    )
                    self.record_orphan_row(
                        table_name,
                        row,
                        key_name,
                        f"missing {key_name} {row[key_name]}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

        protocol_detail_count = 0
        for row in self.legacy_rows("SELECT * FROM chemotherapy_protocol_details ORDER BY id"):
            try:
                protocol = self.get_protocol(row["chemotherapy_protocol_id"])
            except ChemotherapyProtocol.DoesNotExist:
                self.record_orphan_row(
                    "chemotherapy_protocol_details",
                    row,
                    "chemotherapy_protocol_id",
                    f"missing chemotherapy_protocol_id {row['chemotherapy_protocol_id']}",
                )
                continue
            ChemotherapyProtocolDetail.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "chemotherapy_protocol": protocol,
                    "value": row["value"],
                },
            )
            protocol_detail_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported chemotherapy_protocol_details: {protocol_detail_count}"))

        schedule_children = [
            (
                "radiotherapy_schedule_sites",
                RadiotherapyScheduleSite,
                lambda row: {
                    "radiotherapy_schedule": self.get_radiotherapy(row["radiotherapy_schedule_id"]),
                    "value": self.clean_str(row["value"]),
                },
            ),
            (
                "radiotherapy_schedule_modalities",
                RadiotherapyScheduleModality,
                lambda row: {
                    "radiotherapy_schedule": self.get_radiotherapy(row["radiotherapy_schedule_id"]),
                    "value": self.clean_str(row["value"]),
                },
            ),
        ]
        for table_name, model, builder in schedule_children:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                try:
                    defaults = builder(row)
                except RadiotherapySchedule.DoesNotExist:
                    self.record_orphan_row(
                        table_name,
                        row,
                        "radiotherapy_schedule_id",
                        f"missing radiotherapy_schedule_id {row['radiotherapy_schedule_id']}",
                    )
                    continue
                model.objects.update_or_create(legacy_id=row["id"], defaults=defaults)
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

        laterality_count = 0
        for row in self.legacy_rows("SELECT * FROM surgical_lateralities ORDER BY id"):
            try:
                surgery = self.get_surgery(row["surgery_id"])
            except Surgery.DoesNotExist:
                self.record_orphan_row(
                    "surgical_lateralities",
                    row,
                    "surgery_id",
                    f"missing surgery_id {row['surgery_id']}",
                )
                continue
            SurgicalLaterality.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "surgery": surgery,
                    "value": row["value"],
                },
            )
            laterality_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported surgical_lateralities: {laterality_count}"))
