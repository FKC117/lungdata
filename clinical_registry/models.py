from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class Patient(SoftDeleteModel):
    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"

    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    registry_id = models.CharField(max_length=32, unique=True, blank=True, null=True)
    legacy_unique_id = models.CharField(max_length=32, blank=True)
    registration_no = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=191)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    nid = models.CharField(max_length=32, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    blood_group = models.CharField(max_length=8, blank=True)
    area = models.TextField(blank=True)
    police_station = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    socio_economic_status = models.CharField(max_length=191, blank=True)
    photo = models.CharField(max_length=55, blank=True)
    passport = models.CharField(max_length=32, blank=True)
    patient_type = models.CharField(max_length=32, blank=True)
    is_draft = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_patients",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "patients"
        ordering = ["name", "registry_id"]
        indexes = [
            models.Index(fields=["registry_id"]),
            models.Index(fields=["legacy_unique_id"]),
            models.Index(fields=["registration_no"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.registry_id})"


class Center(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_centers"
        ordering = ["name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class Doctor(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    bmdc_number = models.CharField(max_length=10, blank=True)
    photo = models.CharField(max_length=55, blank=True)
    center = models.ForeignKey(
        Center,
        on_delete=models.SET_NULL,
        related_name="doctors",
        blank=True,
        null=True,
    )
    password = models.TextField(blank=True)
    status = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = "clinical_doctors"
        ordering = ["name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class DoctorDegree(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="degrees",
    )
    degree = models.CharField(max_length=50)

    class Meta:
        db_table = "clinical_doctor_degrees"
        ordering = ["doctor__name", "degree", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.doctor.name}: {self.degree}"


class DoctorPatient(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="doctor_patients",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="doctor_links",
    )

    class Meta:
        db_table = "clinical_doctor_patients"
        ordering = ["doctor__name", "patient__name", "legacy_id"]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "patient"], name="unique_doctor_patient_link")
        ]

    def __str__(self) -> str:
        return f"{self.doctor.name} -> {self.patient.name}"


class DoctorProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name="linked_profiles",
        blank=True,
        null=True,
    )
    display_name = models.CharField(max_length=191, blank=True)
    designation = models.CharField(max_length=191, blank=True)
    department = models.CharField(max_length=191, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    registration_number = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinical_doctor_profiles"
        ordering = ["display_name", "user__username"]

    def __str__(self) -> str:
        return self.display_name or self.user.get_full_name() or self.user.get_username()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        doctors_group, _ = Group.objects.get_or_create(name="Doctors")
        self.user.groups.add(doctors_group)


class LookupOption(TimeStampedModel):
    name = models.CharField(max_length=191, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class GenderOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_gender_options"


class BloodGroupOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_blood_group_options"


class DistrictOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_district_options"


class SocioEconomicStatusOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_socio_economic_status_options"


class PatientTypeOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_patient_type_options"


class MaritalStatusOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_marital_status_options"


class AlcoholHistoryOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_alcohol_history_options"


class SmokingStatusOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_smoking_status_options"


class TuberculosisStatusOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_tuberculosis_status_options"


class CovidStatusOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_covid_status_options"


class CovidVaccineOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_covid_vaccine_options"


class CovidVaccinationDoseOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_covid_vaccination_dose_options"


class DiagnosisDiseaseGroupOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_diagnosis_disease_group_options"


class DiagnosisDiseaseSubgroupOption(TimeStampedModel):
    group = models.ForeignKey(
        DiagnosisDiseaseGroupOption,
        on_delete=models.CASCADE,
        related_name="subgroups",
    )
    name = models.CharField(max_length=191)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinical_diagnosis_disease_subgroup_options"
        ordering = ["group__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_diagnosis_subgroup_per_group")
        ]

    def __str__(self) -> str:
        return self.name


class DiagnosisPrimarySiteOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_diagnosis_primary_site_options"


class DiagnosisLateralityOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_diagnosis_laterality_options"


class DiagnosisMetastaticSiteOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_diagnosis_metastatic_site_options"


class HistopathologyOption(TimeStampedModel):
    name = models.CharField(max_length=191)
    category = models.CharField(max_length=191)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinical_histopathology_options"
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_histopathology_option")
        ]

    def __str__(self) -> str:
        return f"{self.category}: {self.name}"


class IhcMarkerOption(LookupOption):
    class Meta(LookupOption.Meta):
        db_table = "clinical_ihc_marker_options"


class MolecularPathologyOption(TimeStampedModel):
    group = models.CharField(max_length=191)
    name = models.CharField(max_length=191)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinical_molecular_pathology_options"
        ordering = ["group", "name"]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_molecular_pathology_option")
        ]

    def __str__(self) -> str:
        return f"{self.group}: {self.name}"


class PoliceStationOption(TimeStampedModel):
    name = models.CharField(max_length=191)
    district = models.ForeignKey(
        DistrictOption,
        on_delete=models.CASCADE,
        related_name="police_stations",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clinical_police_station_options"
        ordering = ["district__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["district", "name"], name="unique_police_station_per_district")
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.district.name}"


class ClinicalObservation(SoftDeleteModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="observations")
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name="observations",
        blank=True,
        null=True,
    )
    center = models.ForeignKey(
        Center,
        on_delete=models.SET_NULL,
        related_name="observations",
        blank=True,
        null=True,
    )
    time = models.DateTimeField(blank=True, null=True)
    observed_at = models.DateTimeField(blank=True, null=True)
    registration_no = models.CharField(max_length=64, blank=True)
    consulting_doctor_name = models.CharField(max_length=191, blank=True)
    center_name = models.CharField(max_length=191, blank=True)
    cancer_type = models.CharField(max_length=191, blank=True)
    diagnosis_disease_group = models.CharField(max_length=191, blank=True)
    diagnosis_subgroup = models.CharField(max_length=191, blank=True)
    diagnosis_primary_site = models.CharField(max_length=191, blank=True)
    diagnosis_laterility = models.CharField(max_length=191, blank=True)
    diagnosis_laterality = models.CharField(max_length=191, blank=True)
    grade = models.CharField(max_length=191, blank=True)
    laterality = models.TextField(blank=True)
    laterality_notes = models.TextField(blank=True)
    is_draft = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_observations",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "patient_observations"
        ordering = ["-observed_at", "-id"]
        indexes = [
            models.Index(fields=["registration_no"]),
            models.Index(fields=["observed_at"]),
        ]

    def __str__(self) -> str:
        return self.registration_no or f"Observation {self.pk}"


class DoctorRecognitionRecord(models.Model):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    group = models.CharField(max_length=191)
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_doctor_recognition_records"
        ordering = ["group", "value", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.group}: {self.value}"


class LegacyUser(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)
    email = models.EmailField(unique=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    password = models.CharField(max_length=191)
    status = models.CharField(max_length=25)
    remember_token = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "clinical_legacy_users"
        ordering = ["name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class LegacyImportAnomaly(TimeStampedModel):
    class ResolutionStatus(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWED = "reviewed", "Reviewed"
        RESOLVED = "resolved", "Resolved"

    source_table = models.CharField(max_length=191)
    legacy_row_id = models.PositiveBigIntegerField()
    missing_reference_field = models.CharField(max_length=191)
    missing_reference_id = models.PositiveBigIntegerField(blank=True, null=True)
    reason = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)
    resolution_status = models.CharField(
        max_length=16,
        choices=ResolutionStatus.choices,
        default=ResolutionStatus.OPEN,
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "legacy_import_anomalies"
        ordering = ["source_table", "legacy_row_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_table", "legacy_row_id", "missing_reference_field"],
                name="unique_legacy_import_anomaly",
            )
        ]

    def __str__(self) -> str:
        return f"{self.source_table} row {self.legacy_row_id}: {self.reason}"


class AnalyticsAuditEvent(TimeStampedModel):
    """Non-clinical audit trail for analytics access and cohort exports."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_audit_events",
    )
    action = models.CharField(max_length=64)
    filters = models.JSONField(default=dict)

    class Meta:
        db_table = "clinical_analytics_audit_events"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} by {self.user_id or 'unknown'}"


class LegacyNamedRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)

    class Meta:
        abstract = True
        ordering = ["name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class DiagnosisDiseaseGroupRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_diagnosis_disease_group_records"


class DiagnosisDiseaseSubgroupRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    diagnosis_disease_group_record = models.ForeignKey(
        DiagnosisDiseaseGroupRecord,
        on_delete=models.CASCADE,
        related_name="subgroups",
    )
    name = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_diagnosis_disease_subgroup_records"
        ordering = ["diagnosis_disease_group_record__name", "name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class DiagnosisPrimarySiteRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_diagnosis_primary_site_records"


class DiagnosisLaterilityRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_diagnosis_laterility_records"


class DiagnosisMetastaticSiteRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_diagnosis_metastatic_site_records"


class HistopathologyRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)
    type = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_histopathology_records"
        ordering = ["type", "name", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.type}: {self.name}"


class IhcRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_ihc_records"


class MolecularPathologyRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    group = models.CharField(max_length=191)
    name = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_molecular_pathology_records"
        ordering = ["group", "name", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.group}: {self.name}"


class ExonRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    molecular_pathology_record = models.ForeignKey(
        MolecularPathologyRecord,
        on_delete=models.CASCADE,
        related_name="exons",
    )
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_exon_records"
        ordering = ["molecular_pathology_record__name", "value", "legacy_id"]

    def __str__(self) -> str:
        return self.value


class CancerMarkerRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=191)
    unit = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_cancer_marker_records"
        ordering = ["name", "legacy_id"]

    def __str__(self) -> str:
        return self.name


class SocioEconomicStatusRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_socio_economic_status_records"


class CovidVaccineCompanyRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_covid_vaccine_company_records"


class ChemotherapyProtocolRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_chemotherapy_protocol_records"


class ChemotherapyModalityRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_chemotherapy_modality_records"


class RadiotherapyScheduleRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    type = models.CharField(max_length=191)
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_radiotherapy_schedule_records"
        ordering = ["type", "value", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.type}: {self.value}"


class RadiotherapyScheduleIntentRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    value = models.TextField()

    class Meta:
        db_table = "clinical_radiotherapy_schedule_intent_records"
        ordering = ["value", "legacy_id"]

    def __str__(self) -> str:
        return self.value


class SurgeryModalityRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_surgery_modality_records"


class SurgicalLateralityRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_surgical_laterality_records"
        ordering = ["value", "legacy_id"]

    def __str__(self) -> str:
        return self.value


class SurvivalStatusRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_survival_status_records"


class DiseaseProgressionStatusRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_disease_progression_status_records"


class LineOfTreatmentRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_line_of_treatment_records"


class ResponseRateRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    type = models.CharField(max_length=191)
    group = models.CharField(max_length=191)
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_response_rate_records"
        ordering = ["type", "group", "value", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.type} / {self.group}: {self.value}"


class ResponseRateCalculationRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    target_lasion = models.CharField(max_length=191)
    non_target_lasion = models.CharField(max_length=191)
    new_lasion = models.CharField(max_length=191)
    result = models.CharField(max_length=191)
    type = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_response_rate_calculation_records"
        ordering = ["type", "result", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.type}: {self.result}"


class StagingCalculationRecord(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True)
    t = models.CharField(max_length=191)
    n = models.CharField(max_length=191)
    m = models.CharField(max_length=191)
    result = models.CharField(max_length=191)
    type = models.CharField(max_length=191)

    class Meta:
        db_table = "clinical_staging_calculation_records"
        ordering = ["type", "result", "legacy_id"]

    def __str__(self) -> str:
        return f"{self.type}: {self.result}"


class ComorbidityRecord(LegacyNamedRecord):
    class Meta(LegacyNamedRecord.Meta):
        db_table = "clinical_comorbidity_records"


class PatientHistory(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.OneToOneField(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="history",
    )
    marital_status = models.CharField(max_length=50, blank=True)
    dietary_habit = models.CharField(max_length=191, blank=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    h_o_alcoholism = models.CharField(max_length=191, blank=True)
    alcohol_history = models.CharField(max_length=191, blank=True)
    rt_to_chest = models.CharField(max_length=191, blank=True)
    radiotherapy_to_chest = models.CharField(max_length=191, blank=True)
    cancer_history = models.CharField(max_length=191, blank=True)
    family_cancer_history = models.CharField(max_length=191, blank=True)
    known_mutation = models.CharField(max_length=191, blank=True)
    first_diagnosis_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "patient_histories"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"History for {self.observation}"


class SmokingHistory(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    patient_history = models.ForeignKey(
        PatientHistory,
        on_delete=models.CASCADE,
        related_name="smoking_histories",
    )
    status = models.CharField(max_length=191)
    per_day = models.PositiveIntegerField(blank=True, null=True)
    cigarettes_per_day = models.PositiveIntegerField(blank=True, null=True)
    duration_in_year = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_years = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    packs_per_year = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pack_years = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quit_period = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quit_period_years = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = "smoking_histories"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.status} smoking history"


class TuberculosisHistory(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    patient_history = models.ForeignKey(
        PatientHistory,
        on_delete=models.CASCADE,
        related_name="tb_histories",
    )
    status = models.CharField(max_length=191)
    date = models.DateField(blank=True, null=True)
    treatment = models.TextField(blank=True)

    class Meta:
        db_table = "tb_histories"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"TB history: {self.status}"


class CovidHistory(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    patient_history = models.ForeignKey(
        PatientHistory,
        on_delete=models.CASCADE,
        related_name="covid_histories",
    )
    status = models.CharField(max_length=191)
    date = models.DateField(blank=True, null=True)
    vaccine_name = models.CharField(max_length=191, blank=True)
    vaccination_dose = models.CharField(max_length=191, blank=True)

    class Meta:
        db_table = "covid_histories"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Covid history: {self.status}"


class Diagnosis(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="diagnoses",
    )
    detail = models.TextField(blank=True)

    class Meta:
        db_table = "diagnoses"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.detail[:80] if self.detail else f"Diagnosis {self.pk}"


class DiagnosisMetastaticSite(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="metastatic_sites",
    )
    value = models.CharField(max_length=191, blank=True)

    class Meta:
        db_table = "diagnosis_metastatic_sites"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.value or f"Metastatic site {self.pk}"


class Comorbidity(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="comorbidities",
    )
    detail = models.TextField(blank=True)

    class Meta:
        db_table = "comorbidities"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.detail[:80] if self.detail else f"Comorbidity {self.pk}"


class Histopathology(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="histopathologies",
    )
    detail = models.TextField(blank=True)
    site = models.TextField(blank=True)
    histology_type = models.TextField(blank=True)
    observed_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "histopathologies"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.detail[:80] if self.detail else f"Histopathology {self.pk}"


class MolecularPathology(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="molecular_pathologies",
    )
    specimen = models.CharField(max_length=191, blank=True)
    method = models.CharField(max_length=191, blank=True)
    gene = models.CharField(max_length=191, blank=True)
    exon = models.CharField(max_length=191, blank=True)
    status = models.CharField(max_length=191, blank=True)
    observed_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "molecular_pathologies"
        ordering = ["id"]

    def __str__(self) -> str:
        label = " / ".join(filter(None, [self.gene, self.exon, self.status]))
        return label or f"Molecular pathology {self.pk}"


class CancerMarker(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="cancer_markers",
    )
    name = models.CharField(max_length=191)
    value = models.CharField(max_length=191)
    unit = models.CharField(max_length=191)
    observed_on = models.DateField()

    class Meta:
        db_table = "cancer_markers"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class ClinicalStaging(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="clinical_stagings",
    )
    t = models.CharField(max_length=191, blank=True)
    n = models.CharField(max_length=191, blank=True)
    m = models.CharField(max_length=191, blank=True)
    result = models.CharField(max_length=191, blank=True)
    date = models.DateField(blank=True, null=True)
    staged_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "staging_clinicals"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.result or f"Clinical staging {self.pk}"


class PathologicalStaging(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="pathological_stagings",
    )
    t = models.CharField(max_length=191, blank=True)
    n = models.CharField(max_length=191, blank=True)
    m = models.CharField(max_length=191, blank=True)
    result = models.CharField(max_length=191, blank=True)
    date = models.DateField(blank=True, null=True)
    staged_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "staging_pathologicals"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.result or f"Pathological staging {self.pk}"


class PathologicalStagingDetail(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="pathological_staging_details",
    )
    lvsi = models.CharField(max_length=191, blank=True)
    pni = models.CharField(max_length=191, blank=True)
    margin = models.CharField(max_length=191, blank=True)
    ki67 = models.CharField(max_length=191, blank=True)
    date = models.DateField(blank=True, null=True)
    staged_on = models.DateField()

    class Meta:
        db_table = "staging_pathological_details"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Pathological detail {self.pk}"


class Immunohistochemistry(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="ihc_panels",
    )
    date = models.DateField(blank=True, null=True)
    observed_on = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "ihcs"
        ordering = ["id"]
        verbose_name_plural = "immunohistochemistry panels"

    def __str__(self) -> str:
        return f"IHC {self.observed_on or self.pk}"


class IHCDetail(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    ihc = models.ForeignKey(
        Immunohistochemistry,
        on_delete=models.CASCADE,
        related_name="details",
    )
    type = models.CharField(max_length=191, blank=True)
    marker_type = models.CharField(max_length=191)
    value = models.CharField(max_length=191, blank=True)

    class Meta:
        db_table = "ihc_details"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.marker_type}: {self.value}"


class TreatmentCycle(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="treatment_cycles",
    )
    current_chemo_protocol = models.TextField(blank=True)
    chemo_cycle_no = models.CharField(max_length=191, blank=True)
    chemo_detail = models.TextField(blank=True)
    chemo_starting_date = models.DateField(blank=True, null=True)
    chemo_end_date = models.DateField(blank=True, null=True)
    line_of_treatment = models.CharField(max_length=191, blank=True)
    disease_progression_status = models.CharField(max_length=191, blank=True)
    disease_progression_status_date = models.DateField(blank=True, null=True)
    survival_status = models.CharField(max_length=191, blank=True)
    survival_status_date = models.DateField(blank=True, null=True)
    recist_1_target_lasion = models.CharField(max_length=191, blank=True)
    recist_1_target_lesion = models.CharField(max_length=191, blank=True)
    recist_1_non_target_lasion = models.CharField(max_length=191, blank=True)
    recist_1_non_target_lesion = models.CharField(max_length=191, blank=True)
    recist_1_new_lasion = models.CharField(max_length=191, blank=True)
    recist_1_new_lesion = models.CharField(max_length=191, blank=True)
    recist_1_result = models.CharField(max_length=191, blank=True)
    recist_1_date = models.DateField(blank=True, null=True)
    recist_1_method_of_estimation = models.CharField(max_length=191, blank=True)
    irecist_target_lasion = models.CharField(max_length=191, blank=True)
    irecist_target_lesion = models.CharField(max_length=191, blank=True)
    irecist_non_target_lasion = models.CharField(max_length=191, blank=True)
    irecist_non_target_lesion = models.CharField(max_length=191, blank=True)
    irecist_new_lasion = models.CharField(max_length=191, blank=True)
    irecist_new_lesion = models.CharField(max_length=191, blank=True)
    irecist_result = models.CharField(max_length=191, blank=True)
    irecist_date = models.DateField(blank=True, null=True)
    irecist_method_of_estimation = models.CharField(max_length=191, blank=True)
    pathological_response_rate_target_lasion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_target_lesion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_non_target_lasion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_non_target_lesion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_new_lasion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_new_lesion = models.CharField(max_length=191, blank=True)
    pathological_response_rate_result = models.CharField(max_length=191, blank=True)
    pathological_response_rate_date = models.DateField(blank=True, null=True)
    pathological_method_of_estimation = models.CharField(max_length=191, blank=True)
    pfs = models.CharField(max_length=191, blank=True)
    progression_free_survival = models.CharField(max_length=191, blank=True)
    overall_survival = models.CharField(max_length=191, blank=True)

    class Meta:
        db_table = "patient_observation_details"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Cycle {self.chemo_cycle_no or self.pk} for {self.observation}"


class TreatmentCycleProgressionSite(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    treatment_cycle = models.ForeignKey(
        TreatmentCycle,
        on_delete=models.CASCADE,
        related_name="progression_sites",
    )
    type = models.CharField(max_length=191, blank=True)
    site_type = models.CharField(max_length=191)
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "patient_observation_response_rate_progression_sites"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.site_type}: {self.value}"


class ChemotherapyProtocol(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    treatment_cycle = models.ForeignKey(
        TreatmentCycle,
        on_delete=models.CASCADE,
        related_name="chemotherapy_protocols",
    )
    cycle_no = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    type = models.CharField(max_length=191, blank=True)
    protocol_type = models.CharField(max_length=191)

    class Meta:
        db_table = "chemotherapy_protocols"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.protocol_type


class ChemotherapyProtocolDetail(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    chemotherapy_protocol = models.ForeignKey(
        ChemotherapyProtocol,
        on_delete=models.CASCADE,
        related_name="details",
    )
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "chemotherapy_protocol_details"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.value


class ChemotherapyModality(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    treatment_cycle = models.ForeignKey(
        TreatmentCycle,
        on_delete=models.CASCADE,
        related_name="chemotherapy_modalities",
    )
    detail = models.CharField(max_length=191)

    class Meta:
        db_table = "chemotherapy_modalities"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.detail


class PastTreatmentHistory(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="past_treatment_histories",
    )
    detail = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "past_treatment_histories"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.detail[:80] if self.detail else f"Past treatment {self.pk}"


class RadiotherapySchedule(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="radiotherapy_schedules",
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    intent = models.TextField(blank=True)
    fraction = models.TextField(blank=True)
    fraction_number = models.TextField(blank=True)
    total_dose = models.TextField(blank=True)

    class Meta:
        db_table = "radiotherapy_schedules"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Radiotherapy {self.start_date or self.pk}"


class RadiotherapyScheduleSite(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    radiotherapy_schedule = models.ForeignKey(
        RadiotherapySchedule,
        on_delete=models.CASCADE,
        related_name="sites",
    )
    value = models.CharField(max_length=191, blank=True)

    class Meta:
        db_table = "radiotherapy_schedule_sites"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.value or f"Site {self.pk}"


class RadiotherapyScheduleModality(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    radiotherapy_schedule = models.ForeignKey(
        RadiotherapySchedule,
        on_delete=models.CASCADE,
        related_name="modalities",
    )
    value = models.TextField(blank=True)

    class Meta:
        db_table = "radiotherapy_schedule_modalities"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.value or f"Modality {self.pk}"


class Surgery(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    observation = models.ForeignKey(
        ClinicalObservation,
        on_delete=models.CASCADE,
        related_name="surgeries",
    )
    surgery_date = models.DateField()
    modality = models.TextField(blank=True)

    class Meta:
        db_table = "surgeries"
        ordering = ["id"]
        verbose_name_plural = "surgeries"

    def __str__(self) -> str:
        return f"Surgery {self.surgery_date}"


class SurgicalLaterality(TimeStampedModel):
    legacy_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    surgery = models.ForeignKey(
        Surgery,
        on_delete=models.CASCADE,
        related_name="lateralities",
    )
    value = models.CharField(max_length=191)

    class Meta:
        db_table = "surgical_lateralities"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.value
