from django.core.management.base import BaseCommand
from django.db import connections, transaction

from clinical_registry.models import (
    AlcoholHistoryOption,
    BloodGroupOption,
    CovidStatusOption,
    CovidVaccinationDoseOption,
    CovidVaccineOption,
    DiagnosisDiseaseGroupOption,
    DiagnosisDiseaseSubgroupOption,
    DiagnosisLateralityOption,
    DiagnosisMetastaticSiteOption,
    DiagnosisPrimarySiteOption,
    DistrictOption,
    GenderOption,
    HistopathologyOption,
    IhcMarkerOption,
    MaritalStatusOption,
    MolecularPathologyOption,
    PatientTypeOption,
    PoliceStationOption,
    SmokingStatusOption,
    SocioEconomicStatusOption,
    TuberculosisStatusOption,
)


class Command(BaseCommand):
    help = "Import canonical lookup options from the legacy MySQL database into Django-managed lookup tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Clear existing canonical lookup options before importing.",
        )

    def handle(self, *args, **options):
        if options["replace"]:
            self.stdout.write("Clearing canonical lookup tables before import...")
            self._clear_tables()

        with transaction.atomic():
            self._import_genders()
            self._import_blood_groups()
            self._import_districts_and_police_stations()
            self._import_socio_economic_statuses()
            self._import_patient_types()
            self._import_history_options()
            self._import_diagnosis_options()

        self.stdout.write(self.style.SUCCESS("Canonical lookup option import completed successfully."))
        self._print_summary()

    def legacy_rows(self, query):
        with connections["legacy"].cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(columns, row))

    def _clear_tables(self):
        DiagnosisDiseaseSubgroupOption.objects.all().delete()
        DiagnosisDiseaseGroupOption.objects.all().delete()
        DiagnosisPrimarySiteOption.objects.all().delete()
        DiagnosisLateralityOption.objects.all().delete()
        DiagnosisMetastaticSiteOption.objects.all().delete()
        HistopathologyOption.objects.all().delete()
        IhcMarkerOption.objects.all().delete()
        MolecularPathologyOption.objects.all().delete()
        PoliceStationOption.objects.all().delete()
        DistrictOption.objects.all().delete()
        CovidVaccinationDoseOption.objects.all().delete()
        CovidVaccineOption.objects.all().delete()
        CovidStatusOption.objects.all().delete()
        TuberculosisStatusOption.objects.all().delete()
        SmokingStatusOption.objects.all().delete()
        AlcoholHistoryOption.objects.all().delete()
        MaritalStatusOption.objects.all().delete()
        SocioEconomicStatusOption.objects.all().delete()
        PatientTypeOption.objects.all().delete()
        BloodGroupOption.objects.all().delete()
        GenderOption.objects.all().delete()

    def _clean(self, value):
        if value is None:
            return ""
        return str(value).strip()

    def _normalize_marital_status(self, value):
        cleaned = self._clean(value)
        if cleaned.lower() == "vegetarin":
            return ""
        return cleaned

    def _normalize_smoking_status(self, value):
        cleaned = self._clean(value)
        if cleaned.lower() == "yes":
            return "Smoker"
        return cleaned

    def _import_genders(self):
        values = {
            self._clean(row["gender"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT gender
                FROM patients
                WHERE COALESCE(TRIM(gender), '') <> ''
                ORDER BY gender
                """
            )
        }
        for value in sorted(values):
            GenderOption.objects.update_or_create(name=value, defaults={"is_active": True})

    def _import_blood_groups(self):
        values = {
            self._clean(row["blood_group"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT blood_group
                FROM patients
                WHERE COALESCE(TRIM(blood_group), '') <> ''
                ORDER BY blood_group
                """
            )
        }
        if not any(values):
            values = {
                "A positive",
                "A negative",
                "B positive",
                "B negative",
                "AB positive",
                "AB negative",
                "O positive",
                "O negative",
            }
        for value in sorted(item for item in values if item):
            BloodGroupOption.objects.update_or_create(name=value, defaults={"is_active": True})

    def _import_districts_and_police_stations(self):
        district_names = set()
        station_pairs = set()

        for row in self.legacy_rows(
            """
            SELECT DISTINCT district, name
            FROM police_stations
            WHERE COALESCE(TRIM(district), '') <> ''
              AND COALESCE(TRIM(name), '') <> ''
            ORDER BY district, name
            """
        ):
            district_name = self._clean(row["district"])
            station_name = self._clean(row["name"])
            if district_name:
                district_names.add(district_name)
            if district_name and station_name:
                station_pairs.add((district_name, station_name))

        for row in self.legacy_rows(
            """
            SELECT DISTINCT district, police_station
            FROM patients
            WHERE COALESCE(TRIM(district), '') <> ''
               OR COALESCE(TRIM(police_station), '') <> ''
            """
        ):
            district_name = self._clean(row["district"])
            station_name = self._clean(row["police_station"])
            if district_name:
                district_names.add(district_name)
            if district_name and station_name:
                station_pairs.add((district_name, station_name))

        district_map = {}
        for district_name in sorted(district_names):
            district, _created = DistrictOption.objects.update_or_create(
                name=district_name,
                defaults={"is_active": True},
            )
            district_map[district_name] = district

        for district_name, station_name in sorted(station_pairs):
            district = district_map[district_name]
            PoliceStationOption.objects.update_or_create(
                district=district,
                name=station_name,
                defaults={"is_active": True},
            )

    def _import_socio_economic_statuses(self):
        values = {
            self._clean(row["name"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT name
                FROM socio_economic_status_records
                WHERE COALESCE(TRIM(name), '') <> ''
                ORDER BY name
                """
            )
        }
        for row in self.legacy_rows(
            """
            SELECT DISTINCT socio_economic_status
            FROM patients
            WHERE COALESCE(TRIM(socio_economic_status), '') <> ''
            ORDER BY socio_economic_status
            """
        ):
            values.add(self._clean(row["socio_economic_status"]))
        for value in sorted(item for item in values if item):
            SocioEconomicStatusOption.objects.update_or_create(name=value, defaults={"is_active": True})

    def _import_patient_types(self):
        values = {
            self._clean(row["type"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT type
                FROM patients
                WHERE COALESCE(TRIM(type), '') <> ''
                ORDER BY type
                """
            )
        }
        for value in sorted(item for item in values if item):
            PatientTypeOption.objects.update_or_create(name=value, defaults={"is_active": True})

    def _import_history_options(self):
        marital_values = {
            self._normalize_marital_status(row["marital_status"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT marital_status
                FROM patient_histories
                WHERE COALESCE(TRIM(marital_status), '') <> ''
                ORDER BY marital_status
                """
            )
        }
        for value in sorted(item for item in marital_values if item):
            MaritalStatusOption.objects.update_or_create(name=value, defaults={"is_active": True})

        alcohol_values = {
            self._clean(row["h_o_alcoholism"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT h_o_alcoholism
                FROM patient_histories
                WHERE COALESCE(TRIM(h_o_alcoholism), '') <> ''
                ORDER BY h_o_alcoholism
                """
            )
        }
        for value in sorted(item for item in alcohol_values if item):
            AlcoholHistoryOption.objects.update_or_create(name=value, defaults={"is_active": True})

        smoking_values = {
            self._normalize_smoking_status(row["status"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT status
                FROM smoking_histories
                WHERE COALESCE(TRIM(status), '') <> ''
                ORDER BY status
                """
            )
        }
        for value in sorted(item for item in smoking_values if item):
            SmokingStatusOption.objects.update_or_create(name=value, defaults={"is_active": True})

        tb_values = {
            self._clean(row["status"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT status
                FROM tb_histories
                WHERE COALESCE(TRIM(status), '') <> ''
                ORDER BY status
                """
            )
        }
        for value in sorted(item for item in tb_values if item):
            TuberculosisStatusOption.objects.update_or_create(name=value, defaults={"is_active": True})

        covid_status_values = {
            self._clean(row["status"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT status
                FROM covid_histories
                WHERE COALESCE(TRIM(status), '') <> ''
                ORDER BY status
                """
            )
        }
        for value in sorted(item for item in covid_status_values if item):
            CovidStatusOption.objects.update_or_create(name=value, defaults={"is_active": True})

        covid_vaccine_values = {
            self._clean(row["name"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT name
                FROM covid_vaccine_company_records
                WHERE COALESCE(TRIM(name), '') <> ''
                ORDER BY name
                """
            )
        }
        for value in sorted(item for item in covid_vaccine_values if item):
            CovidVaccineOption.objects.update_or_create(name=value, defaults={"is_active": True})

        covid_dose_values = {
            self._clean(row["vaccination_dose"])
            for row in self.legacy_rows(
                """
                SELECT DISTINCT vaccination_dose
                FROM covid_histories
                WHERE COALESCE(TRIM(vaccination_dose), '') <> ''
                ORDER BY vaccination_dose
                """
            )
        }
        for value in sorted(item for item in covid_dose_values if item):
            CovidVaccinationDoseOption.objects.update_or_create(name=value, defaults={"is_active": True})

    def _import_diagnosis_options(self):
        group_map = {}
        for row in self.legacy_rows(
            """
            SELECT id, name
            FROM diagnosis_disease_group_records
            WHERE COALESCE(TRIM(name), '') <> ''
            ORDER BY id
            """
        ):
            group = DiagnosisDiseaseGroupOption.objects.update_or_create(
                name=self._clean(row["name"]),
                defaults={"is_active": True},
            )[0]
            group_map[row["id"]] = group

        for row in self.legacy_rows(
            """
            SELECT diagnosis_disease_group_record_id, name
            FROM diagnosis_disease_subgroup_records
            WHERE COALESCE(TRIM(name), '') <> ''
            ORDER BY diagnosis_disease_group_record_id, name
            """
        ):
            group = group_map.get(row["diagnosis_disease_group_record_id"])
            if not group:
                continue
            DiagnosisDiseaseSubgroupOption.objects.update_or_create(
                group=group,
                name=self._clean(row["name"]),
                defaults={"is_active": True},
            )

        for model, table_name in [
            (DiagnosisPrimarySiteOption, "diagnosis_primary_site_records"),
            (DiagnosisLateralityOption, "diagnosis_laterility_records"),
            (DiagnosisMetastaticSiteOption, "diagnosis_metastatic_site_records"),
            (IhcMarkerOption, "ihc_records"),
        ]:
            for row in self.legacy_rows(
                f"""
                SELECT name
                FROM {table_name}
                WHERE COALESCE(TRIM(name), '') <> ''
                ORDER BY name
                """
            ):
                model.objects.update_or_create(
                    name=self._clean(row["name"]),
                    defaults={"is_active": True},
                )

        for row in self.legacy_rows(
            """
            SELECT name, type
            FROM histopathology_records
            WHERE COALESCE(TRIM(name), '') <> ''
              AND COALESCE(TRIM(type), '') <> ''
            ORDER BY type, name
            """
        ):
            HistopathologyOption.objects.update_or_create(
                category=self._clean(row["type"]),
                name=self._clean(row["name"]),
                defaults={"is_active": True},
            )

        for row in self.legacy_rows(
            """
            SELECT `group`, name
            FROM molecular_pathology_records
            WHERE COALESCE(TRIM(`group`), '') <> ''
              AND COALESCE(TRIM(name), '') <> ''
            ORDER BY `group`, name
            """
        ):
            MolecularPathologyOption.objects.update_or_create(
                group=self._clean(row["group"]),
                name=self._clean(row["name"]),
                defaults={"is_active": True},
            )

    def _print_summary(self):
        summary = {
            "GenderOption": GenderOption.objects.count(),
            "BloodGroupOption": BloodGroupOption.objects.count(),
            "DistrictOption": DistrictOption.objects.count(),
            "PoliceStationOption": PoliceStationOption.objects.count(),
            "SocioEconomicStatusOption": SocioEconomicStatusOption.objects.count(),
            "PatientTypeOption": PatientTypeOption.objects.count(),
            "MaritalStatusOption": MaritalStatusOption.objects.count(),
            "AlcoholHistoryOption": AlcoholHistoryOption.objects.count(),
            "SmokingStatusOption": SmokingStatusOption.objects.count(),
            "TuberculosisStatusOption": TuberculosisStatusOption.objects.count(),
            "CovidStatusOption": CovidStatusOption.objects.count(),
            "CovidVaccineOption": CovidVaccineOption.objects.count(),
            "CovidVaccinationDoseOption": CovidVaccinationDoseOption.objects.count(),
            "DiagnosisDiseaseGroupOption": DiagnosisDiseaseGroupOption.objects.count(),
            "DiagnosisDiseaseSubgroupOption": DiagnosisDiseaseSubgroupOption.objects.count(),
            "DiagnosisPrimarySiteOption": DiagnosisPrimarySiteOption.objects.count(),
            "DiagnosisLateralityOption": DiagnosisLateralityOption.objects.count(),
            "DiagnosisMetastaticSiteOption": DiagnosisMetastaticSiteOption.objects.count(),
            "HistopathologyOption": HistopathologyOption.objects.count(),
            "IhcMarkerOption": IhcMarkerOption.objects.count(),
            "MolecularPathologyOption": MolecularPathologyOption.objects.count(),
        }
        for label, count in summary.items():
            self.stdout.write(f"{label}: {count}")
