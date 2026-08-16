from datetime import date

from django.db import transaction
from rest_framework import serializers

from clinical_registry.models import (
    CancerMarker,
    ClinicalObservation,
    ClinicalStaging,
    Comorbidity,
    CovidHistory,
    Diagnosis,
    DiagnosisMetastaticSite,
    Histopathology,
    IHCDetail,
    Immunohistochemistry,
    MolecularPathology,
    Patient,
    PatientHistory,
    PathologicalStaging,
    PathologicalStagingDetail,
    RadiotherapySchedule,
    RadiotherapyScheduleModality,
    RadiotherapyScheduleSite,
    SmokingHistory,
    Surgery,
    SurgicalLaterality,
    TreatmentCycle,
    TuberculosisHistory,
)


class SmokingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SmokingHistory
        fields = (
            "id",
            "status",
            "cigarettes_per_day",
            "duration_years",
            "pack_years",
            "quit_period_years",
        )


class TuberculosisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TuberculosisHistory
        fields = ("id", "status", "date", "treatment")


class CovidHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CovidHistory
        fields = ("id", "status", "date", "vaccine_name", "vaccination_dose")


class PatientHistorySerializer(serializers.ModelSerializer):
    smoking_histories = SmokingHistorySerializer(many=True, read_only=True)
    tb_histories = TuberculosisHistorySerializer(many=True, read_only=True)
    covid_histories = CovidHistorySerializer(many=True, read_only=True)

    class Meta:
        model = PatientHistory
        fields = (
            "id",
            "marital_status",
            "dietary_habit",
            "height_cm",
            "weight_kg",
            "bmi",
            "alcohol_history",
            "radiotherapy_to_chest",
            "family_cancer_history",
            "known_mutation",
            "first_diagnosis_date",
            "smoking_histories",
            "tb_histories",
            "covid_histories",
        )


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ("id", "detail")


class DiagnosisMetastaticSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisMetastaticSite
        fields = ("id", "value")


class ComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidity
        fields = ("id", "detail")


class HistopathologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Histopathology
        fields = ("id", "detail", "site", "histology_type", "observed_on")


class MolecularPathologySerializer(serializers.ModelSerializer):
    class Meta:
        model = MolecularPathology
        fields = ("id", "specimen", "method", "gene", "exon", "status", "observed_on")


class CancerMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerMarker
        fields = ("id", "name", "value", "unit", "observed_on")


class ClinicalStagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalStaging
        fields = ("id", "t", "n", "m", "result", "staged_on")


class PathologicalStagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathologicalStaging
        fields = ("id", "t", "n", "m", "result", "staged_on")


class PathologicalStagingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathologicalStagingDetail
        fields = ("id", "lvsi", "pni", "margin", "ki67", "staged_on")


class IHCDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IHCDetail
        fields = ("id", "marker_type", "value")


class ImmunohistochemistrySerializer(serializers.ModelSerializer):
    details = IHCDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Immunohistochemistry
        fields = ("id", "observed_on", "details")


class RadiotherapyScheduleSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiotherapyScheduleSite
        fields = ("id", "value")


class RadiotherapyScheduleModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiotherapyScheduleModality
        fields = ("id", "value")


class RadiotherapyScheduleSerializer(serializers.ModelSerializer):
    sites = RadiotherapyScheduleSiteSerializer(many=True, read_only=True)
    modalities = RadiotherapyScheduleModalitySerializer(many=True, read_only=True)

    class Meta:
        model = RadiotherapySchedule
        fields = (
            "id",
            "start_date",
            "end_date",
            "intent",
            "fraction",
            "fraction_number",
            "total_dose",
            "sites",
            "modalities",
        )


class SurgicalLateralitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalLaterality
        fields = ("id", "value")


class SurgerySerializer(serializers.ModelSerializer):
    lateralities = SurgicalLateralitySerializer(many=True, read_only=True)

    class Meta:
        model = Surgery
        fields = ("id", "surgery_date", "modality", "lateralities")


class TreatmentCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentCycle
        fields = (
            "id",
            "current_chemo_protocol",
            "chemo_cycle_no",
            "chemo_detail",
            "chemo_starting_date",
            "chemo_end_date",
            "line_of_treatment",
            "disease_progression_status",
            "disease_progression_status_date",
            "survival_status",
            "survival_status_date",
            "recist_1_result",
            "recist_1_date",
            "irecist_result",
            "irecist_date",
            "pathological_response_rate_result",
            "pathological_response_rate_date",
            "progression_free_survival",
            "overall_survival",
        )


class ClinicalObservationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalObservation
        fields = (
            "id",
            "legacy_id",
            "registration_no",
            "observed_at",
            "consulting_doctor_name",
            "center_name",
            "cancer_type",
            "diagnosis_disease_group",
            "diagnosis_subgroup",
            "diagnosis_primary_site",
            "diagnosis_laterality",
            "grade",
            "is_draft",
        )


class ClinicalObservationDetailSerializer(ClinicalObservationSummarySerializer):
    history = PatientHistorySerializer(read_only=True)
    diagnoses = DiagnosisSerializer(many=True, read_only=True)
    metastatic_sites = DiagnosisMetastaticSiteSerializer(many=True, read_only=True)
    comorbidities = ComorbiditySerializer(many=True, read_only=True)
    histopathologies = HistopathologySerializer(many=True, read_only=True)
    molecular_pathologies = MolecularPathologySerializer(many=True, read_only=True)
    cancer_markers = CancerMarkerSerializer(many=True, read_only=True)
    clinical_stagings = ClinicalStagingSerializer(many=True, read_only=True)
    pathological_stagings = PathologicalStagingSerializer(many=True, read_only=True)
    pathological_staging_details = PathologicalStagingDetailSerializer(many=True, read_only=True)
    ihc_panels = ImmunohistochemistrySerializer(many=True, read_only=True)
    treatment_cycles = TreatmentCycleSerializer(many=True, read_only=True)
    radiotherapy_schedules = RadiotherapyScheduleSerializer(many=True, read_only=True)
    surgeries = SurgerySerializer(many=True, read_only=True)

    class Meta(ClinicalObservationSummarySerializer.Meta):
        fields = ClinicalObservationSummarySerializer.Meta.fields + (
            "history",
            "diagnoses",
            "metastatic_sites",
            "comorbidities",
            "histopathologies",
            "molecular_pathologies",
            "cancer_markers",
            "clinical_stagings",
            "pathological_stagings",
            "pathological_staging_details",
            "ihc_panels",
            "treatment_cycles",
            "radiotherapy_schedules",
            "surgeries",
        )


class PatientListSerializer(serializers.ModelSerializer):
    latest_observation = serializers.SerializerMethodField()
    observation_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "legacy_id",
            "registry_id",
            "legacy_unique_id",
            "registration_no",
            "name",
            "phone",
            "age",
            "gender",
            "district",
            "socio_economic_status",
            "observation_count",
            "latest_observation",
        )

    def get_latest_observation(self, obj):
        observation = getattr(obj, "prefetched_latest_observation", None)
        if observation is None:
            observation = obj.observations.order_by("-observed_at", "-id").first()
        if observation is None:
            return None
        return ClinicalObservationSummarySerializer(observation).data


class PatientDetailSerializer(serializers.ModelSerializer):
    observations = ClinicalObservationDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "legacy_id",
            "registry_id",
            "legacy_unique_id",
            "registration_no",
            "name",
            "phone",
            "email",
            "nid",
            "date_of_birth",
            "age",
            "gender",
            "blood_group",
            "area",
            "police_station",
            "district",
            "socio_economic_status",
            "passport",
            "patient_type",
            "is_draft",
            "observations",
        )


class PatientEntryHistorySerializer(serializers.Serializer):
    marital_status = serializers.CharField(required=False, allow_blank=True)
    dietary_habit = serializers.CharField(required=False, allow_blank=True)
    height_cm = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    weight_kg = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    bmi = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    alcohol_history = serializers.CharField(required=False, allow_blank=True)
    radiotherapy_to_chest = serializers.CharField(required=False, allow_blank=True)
    family_cancer_history = serializers.CharField(required=False, allow_blank=True)
    known_mutation = serializers.CharField(required=False, allow_blank=True)
    first_diagnosis_date = serializers.DateField(required=False, allow_null=True)


class SmokingHistoryWriteSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, allow_blank=True)
    cigarettes_per_day = serializers.IntegerField(required=False, allow_null=True)
    duration_years = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    pack_years = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    quit_period_years = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)


class TuberculosisHistoryWriteSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField(required=False, allow_null=True)
    treatment = serializers.CharField(required=False, allow_blank=True)


class CovidHistoryWriteSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField(required=False, allow_null=True)
    vaccine_name = serializers.CharField(required=False, allow_blank=True)
    vaccination_dose = serializers.CharField(required=False, allow_blank=True)


class HistopathologyWriteSerializer(serializers.Serializer):
    detail = serializers.CharField(required=False, allow_blank=True)
    site = serializers.CharField(required=False, allow_blank=True)
    histology_type = serializers.CharField(required=False, allow_blank=True)
    observed_on = serializers.DateField(required=False, allow_null=True)


class MolecularPathologyWriteSerializer(serializers.Serializer):
    specimen = serializers.CharField(required=False, allow_blank=True)
    method = serializers.CharField(required=False, allow_blank=True)
    gene = serializers.CharField(required=False, allow_blank=True)
    exon = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    observed_on = serializers.DateField(required=False, allow_null=True)


class CancerMarkerWriteSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()
    unit = serializers.CharField(required=False, allow_blank=True)
    observed_on = serializers.DateField()


class ClinicalStagingWriteSerializer(serializers.Serializer):
    t = serializers.CharField(required=False, allow_blank=True)
    n = serializers.CharField(required=False, allow_blank=True)
    m = serializers.CharField(required=False, allow_blank=True)
    result = serializers.CharField(required=False, allow_blank=True)
    staged_on = serializers.DateField(required=False, allow_null=True)


class PathologicalStagingWriteSerializer(serializers.Serializer):
    t = serializers.CharField(required=False, allow_blank=True)
    n = serializers.CharField(required=False, allow_blank=True)
    m = serializers.CharField(required=False, allow_blank=True)
    result = serializers.CharField(required=False, allow_blank=True)
    staged_on = serializers.DateField(required=False, allow_null=True)


class PathologicalStagingDetailWriteSerializer(serializers.Serializer):
    lvsi = serializers.CharField(required=False, allow_blank=True)
    pni = serializers.CharField(required=False, allow_blank=True)
    margin = serializers.CharField(required=False, allow_blank=True)
    ki67 = serializers.CharField(required=False, allow_blank=True)
    staged_on = serializers.DateField(required=False, allow_null=True)


class IHCDetailWriteSerializer(serializers.Serializer):
    marker_type = serializers.CharField(required=False, allow_blank=True)
    value = serializers.CharField(required=False, allow_blank=True)


class IHCPanelWriteSerializer(serializers.Serializer):
    observed_on = serializers.DateField(required=False, allow_null=True)
    details = IHCDetailWriteSerializer(many=True, required=False)


class TreatmentCycleWriteSerializer(serializers.Serializer):
    current_chemo_protocol = serializers.CharField(required=False, allow_blank=True)
    chemo_cycle_no = serializers.CharField(required=False, allow_blank=True)
    chemo_detail = serializers.CharField(required=False, allow_blank=True)
    chemo_starting_date = serializers.DateField(required=False, allow_null=True)
    chemo_end_date = serializers.DateField(required=False, allow_null=True)
    line_of_treatment = serializers.CharField(required=False, allow_blank=True)
    disease_progression_status = serializers.CharField(required=False, allow_blank=True)
    disease_progression_status_date = serializers.DateField(required=False, allow_null=True)
    survival_status = serializers.CharField(required=False, allow_blank=True)
    survival_status_date = serializers.DateField(required=False, allow_null=True)


class RadiotherapyScheduleWriteSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    intent = serializers.CharField(required=False, allow_blank=True)
    fraction = serializers.CharField(required=False, allow_blank=True)
    fraction_number = serializers.CharField(required=False, allow_blank=True)
    total_dose = serializers.CharField(required=False, allow_blank=True)
    sites = serializers.ListField(child=serializers.CharField(), required=False)
    modalities = serializers.ListField(child=serializers.CharField(), required=False)


class SurgeryWriteSerializer(serializers.Serializer):
    surgery_date = serializers.DateField()
    modality = serializers.CharField(required=False, allow_blank=True)
    lateralities = serializers.ListField(child=serializers.CharField(), required=False)


class PastTreatmentHistoryWriteSerializer(serializers.Serializer):
    detail = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField(required=False, allow_null=True)


class PatientEntrySerializer(serializers.Serializer):
    registry_id = serializers.CharField(required=False, allow_blank=True)
    legacy_unique_id = serializers.CharField(required=False, allow_blank=True)
    registration_no = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    nid = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=Patient.Gender.choices, required=False, allow_blank=True)
    blood_group = serializers.CharField(required=False, allow_blank=True)
    area = serializers.CharField(required=False, allow_blank=True)
    police_station = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    socio_economic_status = serializers.CharField(required=False, allow_blank=True)
    passport = serializers.CharField(required=False, allow_blank=True)
    patient_type = serializers.CharField(required=False, allow_blank=True)
    patient_is_draft = serializers.BooleanField(required=False, default=False)

    observed_at = serializers.DateTimeField(required=False, allow_null=True)
    consulting_doctor_name = serializers.CharField(required=False, allow_blank=True)
    center_name = serializers.CharField(required=False, allow_blank=True)
    cancer_type = serializers.CharField(required=False, allow_blank=True)
    diagnosis_disease_group = serializers.CharField(required=False, allow_blank=True)
    diagnosis_subgroup = serializers.CharField(required=False, allow_blank=True)
    diagnosis_primary_site = serializers.CharField(required=False, allow_blank=True)
    diagnosis_laterality = serializers.CharField(required=False, allow_blank=True)
    grade = serializers.CharField(required=False, allow_blank=True)
    laterality_notes = serializers.CharField(required=False, allow_blank=True)
    observation_is_draft = serializers.BooleanField(required=False, default=False)

    history = PatientEntryHistorySerializer(required=False)
    smoking_histories = SmokingHistoryWriteSerializer(many=True, required=False)
    tb_histories = TuberculosisHistoryWriteSerializer(many=True, required=False)
    covid_histories = CovidHistoryWriteSerializer(many=True, required=False)
    diagnoses = serializers.ListField(child=serializers.CharField(), required=False)
    metastatic_sites = serializers.ListField(child=serializers.CharField(), required=False)
    comorbidities = serializers.ListField(child=serializers.CharField(), required=False)
    histopathologies = HistopathologyWriteSerializer(many=True, required=False)
    molecular_pathologies = MolecularPathologyWriteSerializer(many=True, required=False)
    cancer_markers = CancerMarkerWriteSerializer(many=True, required=False)
    clinical_staging = ClinicalStagingWriteSerializer(required=False)
    pathological_staging = PathologicalStagingWriteSerializer(required=False)
    pathological_staging_detail = PathologicalStagingDetailWriteSerializer(required=False)
    ihc_panels = IHCPanelWriteSerializer(many=True, required=False)
    treatment_cycles = TreatmentCycleWriteSerializer(many=True, required=False)
    past_treatment_histories = PastTreatmentHistoryWriteSerializer(many=True, required=False)
    radiotherapy_schedules = RadiotherapyScheduleWriteSerializer(many=True, required=False)
    surgeries = SurgeryWriteSerializer(many=True, required=False)

    def _clean_string_list(self, values):
        return [value.strip() for value in values if value and value.strip()]

    def _calculate_age(self, date_of_birth, reference_date):
        years = reference_date.year - date_of_birth.year
        if (reference_date.month, reference_date.day) < (date_of_birth.month, date_of_birth.day):
            years -= 1
        return max(years, 0)

    def _estimate_date_of_birth(self, age_value, reference_date):
        try:
            return reference_date.replace(year=reference_date.year - age_value)
        except ValueError:
            return reference_date.replace(month=2, day=28, year=reference_date.year - age_value)

    def validate(self, attrs):
        history_data = attrs.get("history") or {}
        observed_at = attrs.get("observed_at")
        reference_date = (
            history_data.get("first_diagnosis_date")
            or (observed_at.date() if observed_at else None)
            or date.today()
        )
        date_of_birth = attrs.get("date_of_birth")
        age_value = attrs.get("age")
        if date_of_birth and age_value in ("", None):
            attrs["age"] = self._calculate_age(date_of_birth, date.today())
        elif age_value is not None and not date_of_birth:
            attrs["date_of_birth"] = self._estimate_date_of_birth(age_value, reference_date)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        history_data = validated_data.pop("history", None)
        smoking_histories = validated_data.pop("smoking_histories", [])
        tb_histories = validated_data.pop("tb_histories", [])
        covid_histories = validated_data.pop("covid_histories", [])
        diagnoses = self._clean_string_list(validated_data.pop("diagnoses", []))
        metastatic_sites = self._clean_string_list(validated_data.pop("metastatic_sites", []))
        comorbidities = self._clean_string_list(validated_data.pop("comorbidities", []))
        histopathologies = validated_data.pop("histopathologies", [])
        molecular_pathologies = validated_data.pop("molecular_pathologies", [])
        cancer_markers = validated_data.pop("cancer_markers", [])
        clinical_staging = validated_data.pop("clinical_staging", None)
        pathological_staging = validated_data.pop("pathological_staging", None)
        pathological_staging_detail = validated_data.pop("pathological_staging_detail", None)
        ihc_panels = validated_data.pop("ihc_panels", [])
        treatment_cycles = validated_data.pop("treatment_cycles", [])
        past_treatment_histories = validated_data.pop("past_treatment_histories", [])
        radiotherapy_schedules = validated_data.pop("radiotherapy_schedules", [])
        surgeries = validated_data.pop("surgeries", [])

        patient = Patient.objects.create(
            registry_id=(validated_data.pop("registry_id", "") or "").strip() or None,
            legacy_unique_id=validated_data.pop("legacy_unique_id", ""),
            registration_no=validated_data.pop("registration_no", ""),
            name=validated_data.pop("name"),
            phone=validated_data.pop("phone", ""),
            email=validated_data.pop("email", ""),
            nid=validated_data.pop("nid", ""),
            date_of_birth=validated_data.pop("date_of_birth", None),
            age=validated_data.pop("age", None),
            gender=validated_data.pop("gender", ""),
            blood_group=validated_data.pop("blood_group", ""),
            area=validated_data.pop("area", ""),
            police_station=validated_data.pop("police_station", ""),
            district=validated_data.pop("district", ""),
            socio_economic_status=validated_data.pop("socio_economic_status", ""),
            passport=validated_data.pop("passport", ""),
            patient_type=validated_data.pop("patient_type", ""),
            is_draft=validated_data.pop("patient_is_draft", False),
        )
        if not patient.registry_id:
            patient.registry_id = f"REG-{patient.pk:09d}"
            patient.save(update_fields=["registry_id"])

        observation = ClinicalObservation.objects.create(
            patient=patient,
            observed_at=validated_data.pop("observed_at", None),
            registration_no=patient.registration_no,
            consulting_doctor_name=validated_data.pop("consulting_doctor_name", ""),
            center_name=validated_data.pop("center_name", ""),
            cancer_type=validated_data.pop("cancer_type", ""),
            diagnosis_disease_group=validated_data.pop("diagnosis_disease_group", ""),
            diagnosis_subgroup=validated_data.pop("diagnosis_subgroup", ""),
            diagnosis_primary_site=validated_data.pop("diagnosis_primary_site", ""),
            diagnosis_laterality=validated_data.pop("diagnosis_laterality", ""),
            grade=validated_data.pop("grade", ""),
            laterality_notes=validated_data.pop("laterality_notes", ""),
            is_draft=validated_data.pop("observation_is_draft", False),
        )

        patient_history = None
        if history_data and any(value not in ("", None) for value in history_data.values()):
            patient_history = PatientHistory.objects.create(observation=observation, **history_data)
        elif smoking_histories or tb_histories or covid_histories:
            patient_history = PatientHistory.objects.create(observation=observation)

        if patient_history is not None:
            for smoking_history in smoking_histories:
                if any(value not in ("", None) for value in smoking_history.values()):
                    SmokingHistory.objects.create(patient_history=patient_history, **smoking_history)
            for tb_history in tb_histories:
                if any(value not in ("", None) for value in tb_history.values()):
                    TuberculosisHistory.objects.create(patient_history=patient_history, **tb_history)
            for covid_history in covid_histories:
                if any(value not in ("", None) for value in covid_history.values()):
                    CovidHistory.objects.create(patient_history=patient_history, **covid_history)

        for detail in diagnoses:
            Diagnosis.objects.create(observation=observation, detail=detail)
        for value in metastatic_sites:
            DiagnosisMetastaticSite.objects.create(observation=observation, value=value)
        for detail in comorbidities:
            Comorbidity.objects.create(observation=observation, detail=detail)
        for histopathology in histopathologies:
            if any(value not in ("", None) for value in histopathology.values()):
                Histopathology.objects.create(observation=observation, **histopathology)
        for molecular_pathology in molecular_pathologies:
            if any(value not in ("", None) for value in molecular_pathology.values()):
                MolecularPathology.objects.create(observation=observation, **molecular_pathology)
        for marker in cancer_markers:
            CancerMarker.objects.create(observation=observation, **marker)
        if clinical_staging and any(value not in ("", None) for value in clinical_staging.values()):
            ClinicalStaging.objects.create(observation=observation, **clinical_staging)
        if pathological_staging and any(value not in ("", None) for value in pathological_staging.values()):
            PathologicalStaging.objects.create(observation=observation, **pathological_staging)
        if pathological_staging_detail and any(
            value not in ("", None) for value in pathological_staging_detail.values()
        ):
            PathologicalStagingDetail.objects.create(observation=observation, **pathological_staging_detail)
        for ihc_panel in ihc_panels:
            detail_rows = ihc_panel.pop("details", [])
            if any(value not in ("", None) for value in ihc_panel.values()) or detail_rows:
                panel = Immunohistochemistry.objects.create(observation=observation, **ihc_panel)
                for detail_row in detail_rows:
                    if any(value not in ("", None) for value in detail_row.values()):
                        IHCDetail.objects.create(ihc=panel, **detail_row)
        for cycle in treatment_cycles:
            if any(value not in ("", None) for value in cycle.values()):
                TreatmentCycle.objects.create(observation=observation, **cycle)
        for past_treatment_history in past_treatment_histories:
            if any(value not in ("", None) for value in past_treatment_history.values()):
                PastTreatmentHistory.objects.create(observation=observation, **past_treatment_history)
        for schedule in radiotherapy_schedules:
            sites = self._clean_string_list(schedule.pop("sites", []))
            modalities = self._clean_string_list(schedule.pop("modalities", []))
            if any(value not in ("", None) for value in schedule.values()) or sites or modalities:
                radiotherapy = RadiotherapySchedule.objects.create(observation=observation, **schedule)
                for value in sites:
                    RadiotherapyScheduleSite.objects.create(radiotherapy_schedule=radiotherapy, value=value)
                for value in modalities:
                    RadiotherapyScheduleModality.objects.create(radiotherapy_schedule=radiotherapy, value=value)
        for surgery_data in surgeries:
            lateralities = self._clean_string_list(surgery_data.pop("lateralities", []))
            surgery = Surgery.objects.create(observation=observation, **surgery_data)
            for value in lateralities:
                SurgicalLaterality.objects.create(surgery=surgery, value=value)

        return patient
