from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils import timezone

from clinical_registry.models import (
    CancerMarkerRecord,
    ChemotherapyModalityRecord,
    ChemotherapyProtocolRecord,
    ComorbidityRecord,
    CovidVaccineCompanyRecord,
    DiagnosisDiseaseGroupRecord,
    DiagnosisDiseaseSubgroupRecord,
    DiagnosisLaterilityRecord,
    DiagnosisMetastaticSiteRecord,
    DiagnosisPrimarySiteRecord,
    DiseaseProgressionStatusRecord,
    ExonRecord,
    HistopathologyRecord,
    IhcRecord,
    LineOfTreatmentRecord,
    MolecularPathologyRecord,
    RadiotherapyScheduleIntentRecord,
    RadiotherapyScheduleRecord,
    ResponseRateCalculationRecord,
    ResponseRateRecord,
    SocioEconomicStatusRecord,
    StagingCalculationRecord,
    SurgicalLateralityRecord,
    SurgeryModalityRecord,
    SurvivalStatusRecord,
)


class Command(BaseCommand):
    help = "Import mirrored legacy lookup and record tables from the legacy MySQL database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete mirrored legacy record tables before importing.",
        )

    def handle(self, *args, **options):
        if options["truncate"]:
            self._truncate_target_data()

        with transaction.atomic():
            self.import_simple_named_tables()
            self.import_specialized_tables()
            self.import_related_tables()

        self.stdout.write(self.style.SUCCESS("Legacy record mirror import completed successfully."))

    def legacy_rows(self, query):
        with connections["legacy"].cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(columns, row))

    def clean_timestamp(self, value):
        """Preserve legacy timestamps, falling back only when the source is null."""
        if value is None:
            return timezone.now()
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def _truncate_target_data(self):
        for model in [
            ExonRecord,
            DiagnosisDiseaseSubgroupRecord,
            CancerMarkerRecord,
            ChemotherapyModalityRecord,
            ChemotherapyProtocolRecord,
            ComorbidityRecord,
            CovidVaccineCompanyRecord,
            DiagnosisDiseaseGroupRecord,
            DiagnosisLaterilityRecord,
            DiagnosisMetastaticSiteRecord,
            DiagnosisPrimarySiteRecord,
            DiseaseProgressionStatusRecord,
            HistopathologyRecord,
            IhcRecord,
            LineOfTreatmentRecord,
            MolecularPathologyRecord,
            RadiotherapyScheduleIntentRecord,
            RadiotherapyScheduleRecord,
            ResponseRateCalculationRecord,
            ResponseRateRecord,
            SocioEconomicStatusRecord,
            StagingCalculationRecord,
            SurgicalLateralityRecord,
            SurgeryModalityRecord,
            SurvivalStatusRecord,
        ]:
            model.objects.all().delete()
        self.stdout.write(self.style.WARNING("Mirrored legacy record tables truncated."))

    def import_simple_named_tables(self):
        mapping = [
            ("diagnosis_disease_group_records", DiagnosisDiseaseGroupRecord),
            ("diagnosis_primary_site_records", DiagnosisPrimarySiteRecord),
            ("diagnosis_laterility_records", DiagnosisLaterilityRecord),
            ("diagnosis_metastatic_site_records", DiagnosisMetastaticSiteRecord),
            ("ihc_records", IhcRecord),
            ("socio_economic_status_records", SocioEconomicStatusRecord),
            ("covid_vaccine_company_records", CovidVaccineCompanyRecord),
            ("chemotherapy_protocol_records", ChemotherapyProtocolRecord),
            ("chemotherapy_modality_records", ChemotherapyModalityRecord),
            ("surgery_modality_records", SurgeryModalityRecord),
            ("survival_status_records", SurvivalStatusRecord),
            ("disease_progression_status_records", DiseaseProgressionStatusRecord),
            ("line_of_treatment_records", LineOfTreatmentRecord),
            ("comorbidity_records", ComorbidityRecord),
        ]
        for table_name, model in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                model.objects.update_or_create(
                    legacy_id=row["id"],
                    defaults={
                        "name": row["name"],
                        "created_at": self.clean_timestamp(row.get("created_at")),
                        "updated_at": self.clean_timestamp(row.get("updated_at")),
                    },
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

    def import_specialized_tables(self):
        mapping = [
            (
                "histopathology_records",
                HistopathologyRecord,
                lambda row: {"name": row["name"], "type": row["type"]},
            ),
            (
                "molecular_pathology_records",
                MolecularPathologyRecord,
                lambda row: {"group": row["group"], "name": row["name"]},
            ),
            (
                "cancer_marker_records",
                CancerMarkerRecord,
                lambda row: {"name": row["name"], "unit": row["unit"]},
            ),
            (
                "radiotherapy_schedule_records",
                RadiotherapyScheduleRecord,
                lambda row: {"type": row["type"], "value": row["value"]},
            ),
            (
                "radiotherapy_schedule_intent_records",
                RadiotherapyScheduleIntentRecord,
                lambda row: {"value": row["value"]},
            ),
            (
                "surgical_laterality_records",
                SurgicalLateralityRecord,
                lambda row: {"value": row["value"]},
            ),
            (
                "response_rate_records",
                ResponseRateRecord,
                lambda row: {"type": row["type"], "group": row["group"], "value": row["value"]},
            ),
            (
                "response_rate_calculation_records",
                ResponseRateCalculationRecord,
                lambda row: {
                    "target_lasion": row["target_lasion"] or "",
                    "non_target_lasion": row["non_target_lasion"] or "",
                    "new_lasion": row["new_lasion"] or "",
                    "result": row["result"] or "",
                    "type": row["type"] or "",
                },
            ),
            (
                "staging_calculation_records",
                StagingCalculationRecord,
                lambda row: {
                    "t": row["t"] or "",
                    "n": row["n"] or "",
                    "m": row["m"] or "",
                    "result": row["result"] or "",
                    "type": row["type"] or "",
                },
            ),
        ]
        for table_name, model, builder in mapping:
            count = 0
            for row in self.legacy_rows(f"SELECT * FROM {table_name} ORDER BY id"):
                defaults = builder(row)
                defaults["created_at"] = self.clean_timestamp(row.get("created_at"))
                defaults["updated_at"] = self.clean_timestamp(row.get("updated_at"))
                model.objects.update_or_create(
                    legacy_id=row["id"],
                    defaults=defaults,
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {table_name}: {count}"))

    def import_related_tables(self):
        subgroup_count = 0
        for row in self.legacy_rows("SELECT * FROM diagnosis_disease_subgroup_records ORDER BY id"):
            group = DiagnosisDiseaseGroupRecord.objects.get(
                legacy_id=row["diagnosis_disease_group_record_id"]
            )
            DiagnosisDiseaseSubgroupRecord.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "diagnosis_disease_group_record": group,
                    "name": row["name"],
                    "created_at": self.clean_timestamp(row.get("created_at")),
                    "updated_at": self.clean_timestamp(row.get("updated_at")),
                },
            )
            subgroup_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported diagnosis_disease_subgroup_records: {subgroup_count}"))

        exon_count = 0
        for row in self.legacy_rows("SELECT * FROM exon_records ORDER BY id"):
            molecular_record = MolecularPathologyRecord.objects.get(
                legacy_id=row["molecular_pathology_record_id"]
            )
            ExonRecord.objects.update_or_create(
                legacy_id=row["id"],
                defaults={
                    "molecular_pathology_record": molecular_record,
                    "value": row["value"],
                    "created_at": self.clean_timestamp(row.get("created_at")),
                    "updated_at": self.clean_timestamp(row.get("updated_at")),
                },
            )
            exon_count += 1
        self.stdout.write(self.style.SUCCESS(f"Imported exon_records: {exon_count}"))
