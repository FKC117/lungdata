from django.contrib import admin

from clinical_registry.models import (
    AlcoholHistoryOption,
    BloodGroupOption,
    CancerMarker,
    ChemotherapyModality,
    ChemotherapyProtocol,
    ChemotherapyProtocolDetail,
    ClinicalObservation,
    ClinicalStaging,
    Comorbidity,
    CovidStatusOption,
    CovidVaccinationDoseOption,
    CovidVaccineOption,
    CovidHistory,
    DiagnosisDiseaseGroupOption,
    DiagnosisDiseaseSubgroupOption,
    DiagnosisLateralityOption,
    DiagnosisMetastaticSiteOption,
    DiagnosisPrimarySiteOption,
    DistrictOption,
    Diagnosis,
    DiagnosisMetastaticSite,
    GenderOption,
    Histopathology,
    HistopathologyOption,
    IHCDetail,
    IhcMarkerOption,
    Immunohistochemistry,
    MolecularPathology,
    MolecularPathologyOption,
    MaritalStatusOption,
    PastTreatmentHistory,
    PathologicalStaging,
    PathologicalStagingDetail,
    Patient,
    PatientTypeOption,
    PatientHistory,
    PoliceStationOption,
    RadiotherapySchedule,
    RadiotherapyScheduleModality,
    RadiotherapyScheduleSite,
    SmokingStatusOption,
    SmokingHistory,
    SocioEconomicStatusOption,
    Surgery,
    SurgicalLaterality,
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
