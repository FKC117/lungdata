from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from clinical_registry.models import (
    AlcoholHistoryOption,
    BloodGroupOption,
    CancerMarker,
    CancerMarkerRecord,
    Center,
    ChemotherapyModality,
    ChemotherapyModalityRecord,
    ChemotherapyProtocol,
    ChemotherapyProtocolDetail,
    ChemotherapyProtocolRecord,
    ClinicalObservation,
    ClinicalStaging,
    Comorbidity,
    ComorbidityRecord,
    CovidStatusOption,
    CovidVaccinationDoseOption,
    CovidVaccineOption,
    CovidVaccineCompanyRecord,
    CovidHistory,
    DiagnosisDiseaseGroupRecord,
    DiagnosisDiseaseGroupOption,
    DiagnosisDiseaseSubgroupRecord,
    DiagnosisDiseaseSubgroupOption,
    DiagnosisLaterilityRecord,
    DiagnosisLateralityOption,
    DiagnosisMetastaticSiteRecord,
    DiagnosisMetastaticSiteOption,
    DiagnosisPrimarySiteRecord,
    DiagnosisPrimarySiteOption,
    DiseaseProgressionStatusRecord,
    Doctor,
    DoctorDegree,
    DoctorPatient,
    DoctorProfile,
    DoctorRecognitionRecord,
    DistrictOption,
    Diagnosis,
    DiagnosisMetastaticSite,
    ExonRecord,
    GenderOption,
    Histopathology,
    HistopathologyRecord,
    HistopathologyOption,
    IHCDetail,
    IhcRecord,
    IhcMarkerOption,
    Immunohistochemistry,
    LineOfTreatmentRecord,
    LegacyImportAnomaly,
    LegacyUser,
    MolecularPathology,
    MolecularPathologyRecord,
    MolecularPathologyOption,
    MaritalStatusOption,
    PastTreatmentHistory,
    PathologicalStaging,
    PathologicalStagingDetail,
    Patient,
    PatientTypeOption,
    PatientHistory,
    PoliceStationOption,
    RadiotherapyScheduleIntentRecord,
    RadiotherapyScheduleRecord,
    RadiotherapySchedule,
    RadiotherapyScheduleModality,
    RadiotherapyScheduleSite,
    ResponseRateCalculationRecord,
    ResponseRateRecord,
    SmokingStatusOption,
    SmokingHistory,
    SocioEconomicStatusRecord,
    StagingCalculationRecord,
    SocioEconomicStatusOption,
    Surgery,
    SurgeryModalityRecord,
    SurgicalLateralityRecord,
    SurgicalLaterality,
    SurvivalStatusRecord,
    TreatmentCycle,
    TreatmentCycleProgressionSite,
    TuberculosisStatusOption,
    TuberculosisHistory,
)


class LookupOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)


class LegacyNamedRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "updated_at")
    search_fields = ("name", "legacy_id")
    ordering = ("name", "legacy_id")


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    extra = 0
    fk_name = "user"
    autocomplete_fields = ("doctor",)


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class RegistryUserAdmin(DjangoUserAdmin):
    inlines = [DoctorProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_registry_role",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")

    @admin.display(description="Registry role")
    def get_registry_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return "Admin"
        if hasattr(obj, "doctor_profile") and obj.doctor_profile.is_active:
            return "Doctor"
        if obj.groups.filter(name__in=["Doctor", "Doctors"]).exists():
            return "Doctor"
        return "User"


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "updated_at")
    search_fields = ("name", "legacy_id")
    ordering = ("name", "legacy_id")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "legacy_id",
        "name",
        "designation",
        "department",
        "center",
        "status",
        "updated_at",
    )
    search_fields = ("name", "email", "phone", "bmdc_number", "legacy_id")
    list_filter = ("designation", "department", "status", "center")
    ordering = ("name", "legacy_id")


@admin.register(DoctorDegree)
class DoctorDegreeAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "doctor", "degree", "updated_at")
    search_fields = ("doctor__name", "degree", "legacy_id")
    ordering = ("doctor__name", "degree")


@admin.register(DoctorPatient)
class DoctorPatientAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "doctor", "patient", "updated_at")
    search_fields = ("doctor__name", "patient__name", "patient__registry_id", "legacy_id")
    ordering = ("doctor__name", "patient__name")


@admin.register(DoctorRecognitionRecord)
class DoctorRecognitionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "group", "value")
    search_fields = ("group", "value", "legacy_id")
    list_filter = ("group",)
    ordering = ("group", "value")


@admin.register(LegacyUser)
class LegacyUserAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "email", "status", "updated_at")
    search_fields = ("name", "email", "legacy_id")
    list_filter = ("status",)
    ordering = ("name", "legacy_id")


@admin.register(LegacyImportAnomaly)
class LegacyImportAnomalyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_table",
        "legacy_row_id",
        "missing_reference_field",
        "missing_reference_id",
        "resolution_status",
        "updated_at",
    )
    search_fields = ("source_table", "legacy_row_id", "missing_reference_field", "reason")
    list_filter = ("source_table", "missing_reference_field", "resolution_status")
    ordering = ("source_table", "legacy_row_id")
    readonly_fields = ("payload", "reason", "created_at", "updated_at")


@admin.register(DiagnosisDiseaseGroupRecord)
class DiagnosisDiseaseGroupRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(DiagnosisPrimarySiteRecord)
class DiagnosisPrimarySiteRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(DiagnosisLaterilityRecord)
class DiagnosisLaterilityRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(DiagnosisMetastaticSiteRecord)
class DiagnosisMetastaticSiteRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(IhcRecord)
class IhcRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(SocioEconomicStatusRecord)
class SocioEconomicStatusRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(CovidVaccineCompanyRecord)
class CovidVaccineCompanyRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(ChemotherapyProtocolRecord)
class ChemotherapyProtocolRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(ChemotherapyModalityRecord)
class ChemotherapyModalityRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(SurgeryModalityRecord)
class SurgeryModalityRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(SurvivalStatusRecord)
class SurvivalStatusRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(DiseaseProgressionStatusRecord)
class DiseaseProgressionStatusRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(LineOfTreatmentRecord)
class LineOfTreatmentRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(ComorbidityRecord)
class ComorbidityRecordAdmin(LegacyNamedRecordAdmin):
    pass


@admin.register(DiagnosisDiseaseSubgroupRecord)
class DiagnosisDiseaseSubgroupRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "diagnosis_disease_group_record", "updated_at")
    search_fields = ("name", "diagnosis_disease_group_record__name", "legacy_id")
    list_filter = ("diagnosis_disease_group_record",)
    ordering = ("diagnosis_disease_group_record__name", "name", "legacy_id")


@admin.register(HistopathologyRecord)
class HistopathologyRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "type", "updated_at")
    search_fields = ("name", "type", "legacy_id")
    list_filter = ("type",)
    ordering = ("type", "name", "legacy_id")


@admin.register(MolecularPathologyRecord)
class MolecularPathologyRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "group", "updated_at")
    search_fields = ("name", "group", "legacy_id")
    list_filter = ("group",)
    ordering = ("group", "name", "legacy_id")


@admin.register(ExonRecord)
class ExonRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "value", "molecular_pathology_record", "updated_at")
    search_fields = ("value", "molecular_pathology_record__name", "legacy_id")
    list_filter = ("molecular_pathology_record__group",)
    ordering = ("molecular_pathology_record__name", "value", "legacy_id")


@admin.register(CancerMarkerRecord)
class CancerMarkerRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "name", "unit", "updated_at")
    search_fields = ("name", "unit", "legacy_id")
    ordering = ("name", "legacy_id")


@admin.register(RadiotherapyScheduleRecord)
class RadiotherapyScheduleRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "type", "value", "updated_at")
    search_fields = ("type", "value", "legacy_id")
    list_filter = ("type",)
    ordering = ("type", "value", "legacy_id")


@admin.register(RadiotherapyScheduleIntentRecord)
class RadiotherapyScheduleIntentRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "value", "updated_at")
    search_fields = ("value", "legacy_id")
    ordering = ("value", "legacy_id")


@admin.register(SurgicalLateralityRecord)
class SurgicalLateralityRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "value", "updated_at")
    search_fields = ("value", "legacy_id")
    ordering = ("value", "legacy_id")


@admin.register(ResponseRateRecord)
class ResponseRateRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "type", "group", "value", "updated_at")
    search_fields = ("type", "group", "value", "legacy_id")
    list_filter = ("type", "group")
    ordering = ("type", "group", "value", "legacy_id")


@admin.register(ResponseRateCalculationRecord)
class ResponseRateCalculationRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "type", "result", "updated_at")
    search_fields = ("type", "result", "target_lasion", "non_target_lasion", "new_lasion", "legacy_id")
    list_filter = ("type", "result")
    ordering = ("type", "result", "legacy_id")


@admin.register(StagingCalculationRecord)
class StagingCalculationRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "legacy_id", "type", "t", "n", "m", "result", "updated_at")
    search_fields = ("type", "t", "n", "m", "result", "legacy_id")
    list_filter = ("type", "result")
    ordering = ("type", "result", "legacy_id")


@admin.register(GenderOption)
class GenderOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(BloodGroupOption)
class BloodGroupOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DistrictOption)
class DistrictOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(SocioEconomicStatusOption)
class SocioEconomicStatusOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(PatientTypeOption)
class PatientTypeOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(MaritalStatusOption)
class MaritalStatusOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(AlcoholHistoryOption)
class AlcoholHistoryOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(SmokingStatusOption)
class SmokingStatusOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(TuberculosisStatusOption)
class TuberculosisStatusOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(CovidStatusOption)
class CovidStatusOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(CovidVaccineOption)
class CovidVaccineOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(CovidVaccinationDoseOption)
class CovidVaccinationDoseOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DiagnosisDiseaseGroupOption)
class DiagnosisDiseaseGroupOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DiagnosisPrimarySiteOption)
class DiagnosisPrimarySiteOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DiagnosisLateralityOption)
class DiagnosisLateralityOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DiagnosisMetastaticSiteOption)
class DiagnosisMetastaticSiteOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(IhcMarkerOption)
class IhcMarkerOptionAdmin(LookupOptionAdmin):
    pass


@admin.register(DiagnosisDiseaseSubgroupOption)
class DiagnosisDiseaseSubgroupOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "is_active", "updated_at")
    search_fields = ("name", "group__name")
    list_filter = ("is_active", "group")
    ordering = ("group__name", "name")


@admin.register(HistopathologyOption)
class HistopathologyOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "is_active", "updated_at")
    search_fields = ("name", "category")
    list_filter = ("is_active", "category")
    ordering = ("category", "name")


@admin.register(MolecularPathologyOption)
class MolecularPathologyOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "is_active", "updated_at")
    search_fields = ("name", "group")
    list_filter = ("is_active", "group")
    ordering = ("group", "name")


@admin.register(PoliceStationOption)
class PoliceStationOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "is_active", "updated_at")
    search_fields = ("name", "district__name")
    list_filter = ("is_active", "district")
    ordering = ("district__name", "name")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "registry_id", "legacy_unique_id", "registration_no", "name", "phone", "gender", "district", "is_draft")
    search_fields = ("registry_id", "legacy_unique_id", "registration_no", "name", "phone", "email", "nid")
    list_filter = ("gender", "district", "is_draft")
    ordering = ("name", "registry_id")


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "display_name",
        "user",
        "doctor",
        "designation",
        "department",
        "phone",
        "registration_number",
        "is_active",
    )
    search_fields = (
        "display_name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "doctor__name",
        "designation",
        "department",
        "phone",
        "registration_number",
    )
    list_filter = ("is_active", "department", "doctor__center")
    autocomplete_fields = ("doctor",)
    ordering = ("display_name", "user__username")


@admin.register(ClinicalObservation)
class ClinicalObservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "registration_no",
        "patient",
        "consulting_doctor_name",
        "center_name",
        "cancer_type",
        "observed_at",
        "is_draft",
    )
    search_fields = ("registration_no", "patient__name", "patient__registry_id", "patient__legacy_unique_id", "consulting_doctor_name")
    list_filter = ("cancer_type", "center_name", "is_draft")
    ordering = ("-observed_at", "-id")


@admin.register(PatientHistory)
class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "marital_status", "first_diagnosis_date", "updated_at")
    search_fields = ("observation__registration_no", "observation__patient__name", "observation__patient__registry_id", "observation__patient__legacy_unique_id")
    ordering = ("-id",)


@admin.register(SmokingHistory)
class SmokingHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_history", "status", "cigarettes_per_day", "duration_years", "pack_years")
    search_fields = ("patient_history__observation__patient__name", "status")
    ordering = ("-id",)


@admin.register(TuberculosisHistory)
class TuberculosisHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_history", "status", "date")
    search_fields = ("patient_history__observation__patient__name", "status", "treatment")
    ordering = ("-id",)


@admin.register(CovidHistory)
class CovidHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_history", "status", "date", "vaccine_name", "vaccination_dose")
    search_fields = ("patient_history__observation__patient__name", "status", "vaccine_name")
    ordering = ("-id",)


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "detail", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "detail")
    ordering = ("-id",)


@admin.register(DiagnosisMetastaticSite)
class DiagnosisMetastaticSiteAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "value", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "value")
    ordering = ("-id",)


@admin.register(Comorbidity)
class ComorbidityAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "detail", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "detail")
    ordering = ("-id",)


@admin.register(Histopathology)
class HistopathologyAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "site", "histology_type", "observed_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "detail", "site", "histology_type")
    ordering = ("-id",)


@admin.register(MolecularPathology)
class MolecularPathologyAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "gene", "exon", "status", "observed_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "gene", "exon", "status")
    ordering = ("-id",)


@admin.register(CancerMarker)
class CancerMarkerAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "name", "value", "unit", "observed_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "name", "value", "unit")
    ordering = ("-id",)


@admin.register(ClinicalStaging)
class ClinicalStagingAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "t", "n", "m", "result", "staged_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "result")
    ordering = ("-id",)


@admin.register(PathologicalStaging)
class PathologicalStagingAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "t", "n", "m", "result", "staged_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "result")
    ordering = ("-id",)


@admin.register(PathologicalStagingDetail)
class PathologicalStagingDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "lvsi", "pni", "margin", "ki67", "staged_on")
    search_fields = ("observation__patient__name", "observation__registration_no", "lvsi", "pni", "margin", "ki67")
    ordering = ("-id",)


@admin.register(Immunohistochemistry)
class ImmunohistochemistryAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "observed_on", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no")
    ordering = ("-id",)


@admin.register(IHCDetail)
class IHCDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "ihc", "marker_type", "value", "updated_at")
    search_fields = ("ihc__observation__patient__name", "ihc__observation__registration_no", "marker_type", "value")
    ordering = ("-id",)


@admin.register(TreatmentCycle)
class TreatmentCycleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "observation",
        "chemo_cycle_no",
        "line_of_treatment",
        "disease_progression_status",
        "survival_status",
        "updated_at",
    )
    search_fields = (
        "observation__patient__name",
        "observation__registration_no",
        "current_chemo_protocol",
        "line_of_treatment",
        "survival_status",
    )
    ordering = ("-id",)


@admin.register(TreatmentCycleProgressionSite)
class TreatmentCycleProgressionSiteAdmin(admin.ModelAdmin):
    list_display = ("id", "treatment_cycle", "site_type", "value", "updated_at")
    search_fields = (
        "treatment_cycle__observation__patient__name",
        "treatment_cycle__observation__registration_no",
        "site_type",
        "value",
    )
    ordering = ("-id",)


@admin.register(ChemotherapyProtocol)
class ChemotherapyProtocolAdmin(admin.ModelAdmin):
    list_display = ("id", "treatment_cycle", "protocol_type", "cycle_no", "updated_at")
    search_fields = ("treatment_cycle__observation__patient__name", "protocol_type")
    ordering = ("-id",)


@admin.register(ChemotherapyProtocolDetail)
class ChemotherapyProtocolDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "chemotherapy_protocol", "value", "updated_at")
    search_fields = ("chemotherapy_protocol__protocol_type", "value")
    ordering = ("-id",)


@admin.register(ChemotherapyModality)
class ChemotherapyModalityAdmin(admin.ModelAdmin):
    list_display = ("id", "treatment_cycle", "detail", "updated_at")
    search_fields = ("treatment_cycle__observation__patient__name", "detail")
    ordering = ("-id",)


@admin.register(PastTreatmentHistory)
class PastTreatmentHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "date", "detail", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "detail")
    ordering = ("-id",)


@admin.register(RadiotherapySchedule)
class RadiotherapyScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "start_date", "end_date", "intent", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "intent")
    ordering = ("-id",)


@admin.register(RadiotherapyScheduleSite)
class RadiotherapyScheduleSiteAdmin(admin.ModelAdmin):
    list_display = ("id", "radiotherapy_schedule", "value", "updated_at")
    search_fields = ("radiotherapy_schedule__observation__patient__name", "value")
    ordering = ("-id",)


@admin.register(RadiotherapyScheduleModality)
class RadiotherapyScheduleModalityAdmin(admin.ModelAdmin):
    list_display = ("id", "radiotherapy_schedule", "value", "updated_at")
    search_fields = ("radiotherapy_schedule__observation__patient__name", "value")
    ordering = ("-id",)


@admin.register(Surgery)
class SurgeryAdmin(admin.ModelAdmin):
    list_display = ("id", "observation", "surgery_date", "modality", "updated_at")
    search_fields = ("observation__patient__name", "observation__registration_no", "modality")
    ordering = ("-id",)


@admin.register(SurgicalLaterality)
class SurgicalLateralityAdmin(admin.ModelAdmin):
    list_display = ("id", "surgery", "value", "updated_at")
    search_fields = ("surgery__observation__patient__name", "value")
    ordering = ("-id",)
