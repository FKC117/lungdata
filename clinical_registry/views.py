import csv
from collections import Counter
from datetime import date, datetime, time, timedelta
from statistics import median

from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import BooleanField, CharField, Count, Max, Min, OuterRef, Prefetch, Q, Subquery
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clinical_registry.access import (
    get_linked_legacy_doctor,
    scope_observations_for_user,
    scope_patients_for_user,
    user_can_edit_patient,
    user_is_admin,
)
from clinical_registry.models import (
    AlcoholHistoryOption,
    AnalyticsAuditEvent,
    BloodGroupOption,
    CancerMarker,
    ClinicalObservation,
    CovidStatusOption,
    CovidVaccinationDoseOption,
    CovidVaccineOption,
    DiagnosisDiseaseGroupOption,
    DiagnosisDiseaseSubgroupOption,
    DiagnosisLateralityOption,
    DiagnosisMetastaticSiteOption,
    DiagnosisPrimarySiteOption,
    DoctorProfile,
    DistrictOption,
    GenderOption,
    HistopathologyOption,
    IhcMarkerOption,
    LegacyImportAnomaly,
    MaritalStatusOption,
    MolecularPathologyOption,
    Patient,
    PatientTypeOption,
    PoliceStationOption,
    SmokingStatusOption,
    SocioEconomicStatusOption,
    TuberculosisStatusOption,
    ClinicalStaging,
    ChemotherapyModality,
    Histopathology,
    MolecularPathology,
    RadiotherapySchedule,
    Surgery,
    TreatmentCycle,
)
from clinical_registry.serializers import (
    PatientDetailSerializer,
    PatientEntrySerializer,
    PatientListSerializer,
)


def user_is_in_named_group(user, *group_names):
    return user.groups.filter(name__in=group_names).exists()


def get_user_role(user):
    if user.is_superuser or user.is_staff:
        return "admin"
    if DoctorProfile.objects.filter(user=user, is_active=True).exists():
        return "doctor"
    if user_is_in_named_group(user, "Doctor", "Doctors"):
        return "doctor"
    return "user"


def get_default_redirect_for_role(role):
    if role in {"admin", "doctor", "user"}:
        return "/patients"
    return "/login"


def user_has_role(user, requested_role):
    actual_role = get_user_role(user)
    if requested_role == "admin":
        return actual_role == "admin"
    if requested_role == "doctor":
        return actual_role in {"admin", "doctor"}
    if requested_role == "user":
        return actual_role in {"admin", "doctor", "user"}
    return False


def serialize_user(user):
    role = get_user_role(user)
    linked_doctor = get_linked_legacy_doctor(user)
    return {
        "id": user.id,
        "username": user.get_username(),
        "full_name": user.get_full_name() or user.get_username(),
        "email": user.email,
        "role": role,
        "default_redirect": get_default_redirect_for_role(role),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "legacy_doctor_id": linked_doctor.legacy_id if linked_doctor else None,
        "legacy_doctor_name": linked_doctor.name if linked_doctor else "",
    }


class IsOwnedByRequesterOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if user_is_admin(request.user):
            return True
        if isinstance(obj, Patient):
            return user_can_edit_patient(request.user, obj)
        patient = getattr(obj, "patient", None)
        if patient is not None:
            return user_can_edit_patient(request.user, patient)
        observation = getattr(obj, "observation", None)
        if observation is not None:
            return user_can_edit_patient(request.user, observation.patient)
        patient_history = getattr(obj, "patient_history", None)
        if patient_history is not None:
            return user_can_edit_patient(request.user, patient_history.observation.patient)
        treatment_cycle = getattr(obj, "treatment_cycle", None)
        if treatment_cycle is not None:
            return user_can_edit_patient(request.user, treatment_cycle.observation.patient)
        radiotherapy_schedule = getattr(obj, "radiotherapy_schedule", None)
        if radiotherapy_schedule is not None:
            return user_can_edit_patient(request.user, radiotherapy_schedule.observation.patient)
        surgery = getattr(obj, "surgery", None)
        if surgery is not None:
            return user_can_edit_patient(request.user, surgery.observation.patient)
        ihc = getattr(obj, "ihc", None)
        if ihc is not None:
            return user_can_edit_patient(request.user, ihc.observation.patient)
        owner = getattr(obj, "created_by", None)
        return owner_id_matches(request.user.id, owner)


def owner_id_matches(user_id, owner):
    owner_id = getattr(owner, "id", owner)
    return bool(user_id and owner_id and user_id == owner_id)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "per_page"
    max_page_size = 100


class PatientListQuerysetMixin:
    def get_queryset(self):
        query = (self.request.GET.get("q") or "").strip()
        state = (self.request.GET.get("state") or "").strip().lower()
        sort = (self.request.GET.get("sort") or "name").strip().lower()
        direction = (self.request.GET.get("dir") or "asc").strip().lower()
        latest_observation_qs = ClinicalObservation.objects.order_by("-observed_at", "-id")
        latest_for_annotations = ClinicalObservation.objects.filter(
            patient_id=OuterRef("pk"),
        ).order_by("-observed_at", "-id")
        queryset = (
            Patient.objects.filter(deleted_at__isnull=True)
            .annotate(
                observation_count=Count("observations"),
                latest_observation_is_draft=Subquery(
                    latest_for_annotations.values("is_draft")[:1],
                    output_field=BooleanField(),
                ),
                latest_observation_group=Subquery(
                    latest_for_annotations.values("diagnosis_disease_group")[:1],
                    output_field=CharField(),
                ),
                latest_observation_site=Subquery(
                    latest_for_annotations.values("diagnosis_primary_site")[:1],
                    output_field=CharField(),
                ),
                latest_observation_observed_at=Subquery(
                    latest_for_annotations.values("observed_at")[:1],
                ),
            )
            .prefetch_related(
                Prefetch(
                    "observations",
                    queryset=latest_observation_qs,
                    to_attr="prefetched_observations",
                )
            )
            .order_by("name", "registry_id")
        )
        queryset = scope_patients_for_user(queryset, self.request.user)
        if state == "published":
            queryset = queryset.filter(observations__is_draft=False).distinct()
        elif state == "draft":
            queryset = queryset.filter(observations__is_draft=True).distinct()
        if query:
            queryset = queryset.filter(
                Q(registry_id__icontains=query)
                | Q(legacy_unique_id__icontains=query)
                | Q(registration_no__icontains=query)
                | Q(name__icontains=query)
                | Q(phone__icontains=query)
            )
        sort_map = {
            "name": "name",
            "registry_id": "registry_id",
            "phone": "phone",
            "age": "age",
            "gender": "gender",
            "district": "district",
            "observations": "observation_count",
            "state": "latest_observation_is_draft",
            "disease_group": "latest_observation_group",
        }
        sort_field = sort_map.get(sort, "name")
        prefix = "-" if direction == "desc" else ""
        queryset = queryset.order_by(f"{prefix}{sort_field}", "registry_id")
        return queryset


class PatientListAPIView(PatientListQuerysetMixin, generics.ListAPIView):
    serializer_class = PatientListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            for patient in page:
                patient.prefetched_latest_observation = (
                    patient.prefetched_observations[0] if getattr(patient, "prefetched_observations", []) else None
                )
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        for patient in queryset:
            patient.prefetched_latest_observation = (
                patient.prefetched_observations[0] if getattr(patient, "prefetched_observations", []) else None
            )
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class PatientExportAPIView(PatientListQuerysetMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="patient_registry_export.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Patient Name",
                "Registry ID",
                "Legacy Unique ID",
                "Registration No",
                "Phone",
                "Age",
                "Gender",
                "District",
                "Observation Count",
                "Latest State",
                "Latest Disease Group",
                "Latest Primary Site",
                "Latest Observed At",
            ]
        )
        for patient in queryset.iterator(chunk_size=200):
            latest_observation = (
                patient.prefetched_observations[0]
                if getattr(patient, "prefetched_observations", [])
                else None
            )
            writer.writerow(
                [
                    patient.name,
                    patient.registry_id,
                    patient.legacy_unique_id,
                    patient.registration_no,
                    patient.phone,
                    patient.age,
                    patient.gender,
                    patient.district,
                    patient.observation_count,
                    (
                        "Draft"
                        if latest_observation and latest_observation.is_draft
                        else "Published"
                        if latest_observation
                        else "No observation"
                    ),
                    latest_observation.diagnosis_disease_group if latest_observation else "",
                    latest_observation.diagnosis_primary_site if latest_observation else "",
                    latest_observation.observed_at if latest_observation else "",
                ]
            )
        return response


class PatientDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PatientDetailSerializer
    lookup_field = "registry_id"
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        observation_queryset = (
            ClinicalObservation.objects.select_related()
            .prefetch_related(
                "history__smoking_histories",
                "history__tb_histories",
                "history__covid_histories",
                "diagnoses",
                "metastatic_sites",
                "comorbidities",
                "histopathologies",
                "molecular_pathologies",
                "cancer_markers",
                "clinical_stagings",
                "pathological_stagings",
                "pathological_staging_details",
                "ihc_panels__details",
                "treatment_cycles__chemotherapy_protocols",
                "treatment_cycles__chemotherapy_modalities",
                "radiotherapy_schedules__sites",
                "radiotherapy_schedules__modalities",
                "surgeries__lateralities",
            )
            .order_by("-observed_at", "-id")
        )
        observation_queryset = scope_observations_for_user(observation_queryset, self.request.user)
        queryset = Patient.objects.filter(deleted_at__isnull=True)
        queryset = scope_patients_for_user(queryset, self.request.user)
        return queryset.prefetch_related(
            Prefetch("observations", queryset=observation_queryset)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PatientUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PatientEntrySerializer
    lookup_field = "registry_id"
    permission_classes = [permissions.IsAuthenticated, IsOwnedByRequesterOrAdmin]

    def get_queryset(self):
        queryset = Patient.objects.filter(deleted_at__isnull=True)
        return scope_patients_for_user(queryset, self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}


class DashboardSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patients_qs = scope_patients_for_user(
            Patient.objects.filter(deleted_at__isnull=True),
            request.user,
        )
        observations_qs = scope_observations_for_user(
            ClinicalObservation.objects.filter(deleted_at__isnull=True),
            request.user,
        )
        data = {
            "patients": patients_qs.count(),
            "observations": observations_qs.count(),
            "published_patients": patients_qs.filter(observations__is_draft=False).distinct().count(),
            "draft_patients": patients_qs.filter(observations__is_draft=True).distinct().count(),
            "published_observations": observations_qs.filter(is_draft=False).count(),
            "draft_observations": observations_qs.filter(is_draft=True).count(),
        }
        return Response(data)


class AnalyticsQueryMixin:
    """Shared, read-only patient cohort builder for the analytics endpoints.

    A cohort is one patient per row.  Date filtering uses the date of a published
    clinical observation; clinical values use the most recently recorded nonblank
    value for that patient.  Blank values are always reported as missing, never as
    a negative result.
    """

    def matching_observations(self, request):
        observations = scope_observations_for_user(
            ClinicalObservation.objects.filter(deleted_at__isnull=True, is_draft=False),
            request.user,
        )
        params = request.query_params
        start, end = params.get("start_date"), params.get("end_date")
        if start:
            start_at = timezone.make_aware(
                datetime.combine(date.fromisoformat(start), time.min),
                timezone.get_current_timezone(),
            )
            observations = observations.filter(observed_at__gte=start_at)
        if end:
            end_at = timezone.make_aware(
                datetime.combine(date.fromisoformat(end) + timedelta(days=1), time.min),
                timezone.get_current_timezone(),
            )
            observations = observations.filter(observed_at__lt=end_at)
        for parameter, field in (("center", "center_id"), ("doctor", "doctor_id")):
            if params.get(parameter):
                observations = observations.filter(**{field: params[parameter]})
        if params.get("diagnosis"):
            observations = observations.filter(diagnosis_disease_group__iexact=params["diagnosis"])
        if params.get("stage"):
            observations = observations.filter(clinical_stagings__result__iexact=params["stage"])
        if params.get("biomarker"):
            observations = observations.filter(molecular_pathologies__gene__iexact=params["biomarker"])
        if params.get("treatment"):
            observations = observations.filter(
                treatment_cycles__chemotherapy_modalities__detail__iexact=params["treatment"]
            )
        if params.get("regimen"):
            observations = observations.filter(
                treatment_cycles__current_chemo_protocol__icontains=params["regimen"]
            )
        if params.get("outcome") == "progressed":
            observations = observations.filter(treatment_cycles__disease_progression_status__icontains="progress")
        elif params.get("outcome") == "deceased":
            observations = observations.filter(treatment_cycles__survival_status__icontains="dead")
        return observations.distinct()

    def get_cohort(self, request):
        patient_ids = self.matching_observations(request).values_list("patient_id", flat=True).distinct()
        return Patient.objects.filter(id__in=patient_ids, deleted_at__isnull=True).distinct()

    def analysis_observations(self, request):
        matching = self.matching_observations(request)
        patient_ids = matching.values_list("patient_id", flat=True).distinct()
        return scope_observations_for_user(
            ClinicalObservation.objects.filter(
                patient_id__in=patient_ids,
                deleted_at__isnull=True,
                is_draft=False,
            ),
            request.user,
        )

    @staticmethod
    def latest_nonblank(items, attribute):
        values = [getattr(item, attribute) for item in items if getattr(item, attribute, None)]
        return values[-1] if values else ""

    def patient_rows(self, cohort, observations=None):
        observations = (observations if observations is not None else ClinicalObservation.objects.filter(
            patient__in=cohort, deleted_at__isnull=True, is_draft=False
        )).select_related("center", "doctor").prefetch_related(
            "history__smoking_histories",
            "history__tb_histories",
            "history__covid_histories",
            "clinical_stagings",
            "pathological_stagings",
            "pathological_staging_details",
            "histopathologies",
            "molecular_pathologies",
            "cancer_markers",
            "metastatic_sites",
            "comorbidities",
            "ihc_panels__details",
            "treatment_cycles__chemotherapy_modalities",
            "treatment_cycles__progression_sites",
            "radiotherapy_schedules__sites",
            "radiotherapy_schedules__modalities",
            "surgeries__lateralities",
        ).order_by("patient_id", "observed_at", "id")
        grouped = {}
        for observation in observations:
            grouped.setdefault(observation.patient_id, []).append(observation)
        rows = []
        for patient in cohort:
            records = grouped.get(patient.id, [])
            stages = [stage for record in records for stage in record.clinical_stagings.all()]
            pathological_stages = [stage for record in records for stage in record.pathological_stagings.all()]
            pathological_details = [detail for record in records for detail in record.pathological_staging_details.all()]
            histopathologies = [item for record in records for item in record.histopathologies.all()]
            molecular = [item for record in records for item in record.molecular_pathologies.all()]
            cycles = [item for record in records for item in record.treatment_cycles.all()]
            histories = [record.history for record in records if hasattr(record, "history")]
            smoking = [item for history in histories for item in history.smoking_histories.all()]
            tb_histories = [item for history in histories for item in history.tb_histories.all()]
            covid_histories = [item for history in histories for item in history.covid_histories.all()]
            metastatic_sites = [item for record in records for item in record.metastatic_sites.all()]
            comorbidities = [item for record in records for item in record.comorbidities.all()]
            cancer_markers = [item for record in records for item in record.cancer_markers.all()]
            radiotherapy = [item for record in records for item in record.radiotherapy_schedules.all()]
            surgeries = [item for record in records for item in record.surgeries.all()]
            treatment_modalities = [item for cycle in cycles for item in cycle.chemotherapy_modalities.all()]
            progression_sites = [item for cycle in cycles for item in cycle.progression_sites.all()]
            radiotherapy_sites = [item for schedule in radiotherapy for item in schedule.sites.all()]
            radiotherapy_modalities = [item for schedule in radiotherapy for item in schedule.modalities.all()]
            surgical_lateralities = [item for surgery in surgeries for item in surgery.lateralities.all()]
            ihc_details = [item for record in records for panel in record.ihc_panels.all() for item in panel.details.all()]
            diagnosis_date = min((item.first_diagnosis_date for item in histories if item.first_diagnosis_date), default=None)
            treatment_start = min((item.chemo_starting_date for item in cycles if item.chemo_starting_date), default=None)
            progression_dates = [item.disease_progression_status_date for item in cycles if item.disease_progression_status_date]
            death_dates = [item.survival_status_date for item in cycles if item.survival_status_date and "dead" in item.survival_status.lower()]
            last_follow_up = max((item.observed_at.date() for item in records if item.observed_at), default=None)
            response = self.latest_nonblank(cycles, "recist_1_result") or self.latest_nonblank(cycles, "irecist_result")
            rows.append({
                "patient": patient, "records": records,
                "diagnosis": self.latest_nonblank(records, "diagnosis_disease_group"),
                "primary_site": self.latest_nonblank(records, "diagnosis_primary_site"),
                "diagnosis_subgroup": self.latest_nonblank(records, "diagnosis_subgroup"),
                "diagnosis_laterality": self.latest_nonblank(records, "diagnosis_laterality") or self.latest_nonblank(records, "diagnosis_laterility"),
                "stage": self.latest_nonblank(stages, "result"),
                "pathological_stage": self.latest_nonblank(pathological_stages, "result"),
                "pathological_margin": self.latest_nonblank(pathological_details, "margin"),
                "pathological_lvsi": self.latest_nonblank(pathological_details, "lvsi"),
                "pathological_pni": self.latest_nonblank(pathological_details, "pni"),
                "pathology": (
                    self.latest_nonblank(histopathologies, "histology_type")
                    or self.latest_nonblank(histopathologies, "detail")
                ),
                "grade": self.latest_nonblank(records, "grade"),
                "biomarker": self.latest_nonblank(molecular, "gene"),
                "molecular_status": self.latest_nonblank(molecular, "status"),
                "molecular_exon": self.latest_nonblank(molecular, "exon"),
                "molecular_method": self.latest_nonblank(molecular, "method"),
                "molecular_specimen": self.latest_nonblank(molecular, "specimen"),
                "ihc_marker": self.latest_nonblank(ihc_details, "marker_type"),
                "ki67": self.latest_nonblank(pathological_details, "ki67"),
                "cancer_marker": self.latest_nonblank(cancer_markers, "name"),
                "treatment": self.latest_nonblank(cycles, "current_chemo_protocol"),
                "treatment_line": self.latest_nonblank(cycles, "line_of_treatment"),
                "treatment_modality": self.latest_nonblank(treatment_modalities, "detail"),
                "response": response, "diagnosis_date": diagnosis_date,
                "progression_status": self.latest_nonblank(cycles, "disease_progression_status"),
                "survival_status": self.latest_nonblank(cycles, "survival_status"),
                "metastatic_site": self.latest_nonblank(metastatic_sites, "value"),
                "progression_site": self.latest_nonblank(progression_sites, "value"),
                "radiotherapy_intent": self.latest_nonblank(radiotherapy, "intent"),
                "radiotherapy_site": self.latest_nonblank(radiotherapy_sites, "value"),
                "radiotherapy_modality": self.latest_nonblank(radiotherapy_modalities, "value"),
                "surgery_modality": self.latest_nonblank(surgeries, "modality"),
                "surgery_laterality": self.latest_nonblank(surgical_lateralities, "value"),
                "smoking_status": self.latest_nonblank(smoking, "status"),
                "comorbidity": self.latest_nonblank(comorbidities, "detail"),
                "gender": patient.gender,
                "district": patient.district,
                "socio_economic_status": patient.socio_economic_status,
                "patient_type": patient.patient_type,
                "alcohol_history": self.latest_nonblank(histories, "alcohol_history") or self.latest_nonblank(histories, "h_o_alcoholism"),
                "tb_status": self.latest_nonblank(tb_histories, "status"),
                "covid_status": self.latest_nonblank(covid_histories, "status"),
                "treatment_start": treatment_start, "progression_date": min(progression_dates, default=None),
                "death_date": min(death_dates, default=None), "last_follow_up": last_follow_up,
                "active_treatment": any(not cycle.chemo_end_date for cycle in cycles),
            })
        return rows

    @staticmethod
    def distribution(rows, key):
        counts = Counter(row[key] or "Not recorded" for row in rows)
        return [{"label": label, "count": count} for label, count in counts.most_common()]

    def definitions(self):
        return {
            "cohort": "One patient with at least one published clinical observation matching the filters.",
            "analysis_scope": "Analytics uses the patient journey: all published observations for patients who ever match the cohort filters.",
            "observation_count": "Number of published clinical observations included in the patient journey for the selected cohort.",
            "date_range": "Filters on published clinical-observation date, inclusive.",
            "response_rate": "Patients with a recorded RECIST 1.1 or iRECIST result divided by patients with a treatment record.",
            "pfs": "Descriptive PFS duration: days from first chemotherapy start to recorded progression or death, or last published observation when neither is recorded. This is not a Kaplan–Meier estimate.",
            "os": "Descriptive OS duration: days from first diagnosis to recorded death, or last published observation when death is not recorded. This is not a Kaplan–Meier estimate.",
            "survival_summary": "Median duration is the ordinary median of available patient-level durations; it does not model censoring or estimate a Kaplan–Meier survival curve.",
            "median_months": "Median months are derived from median days ÷ 30.4375 (365.25 ÷ 12), rounded for display.",
            "missing": "Blank, unknown, and unavailable fields remain Not recorded and are excluded from outcome denominators.",
        }

    def audit(self, request, action):
        AnalyticsAuditEvent.objects.create(
            user=request.user,
            action=action,
            filters={key: value for key, value in request.query_params.items() if value},
        )


class AnalyticsFiltersAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_filters")
        cohort = self.get_cohort(request)
        observations = ClinicalObservation.objects.filter(patient__in=cohort, deleted_at__isnull=True, is_draft=False)
        return Response({
            "centers": list(observations.exclude(center__isnull=True).values("center_id", "center__name").distinct().order_by("center__name")),
            "doctors": list(observations.exclude(doctor__isnull=True).values("doctor_id", "doctor__name").distinct().order_by("doctor__name")),
            "diagnoses": list(observations.exclude(diagnosis_disease_group="").values_list("diagnosis_disease_group", flat=True).distinct().order_by("diagnosis_disease_group")),
            "stages": list(ClinicalStaging.objects.filter(observation__in=observations).exclude(result="").values_list("result", flat=True).distinct().order_by("result")),
            "biomarkers": list(MolecularPathology.objects.filter(observation__in=observations).exclude(gene="").values_list("gene", flat=True).distinct().order_by("gene")),
            "treatments": list(
                ChemotherapyModality.objects.filter(treatment_cycle__observation__in=observations)
                .exclude(detail="")
                .values_list("detail", flat=True)
                .distinct()
                .order_by("detail")
            ),
            "regimens": list(
                TreatmentCycle.objects.filter(observation__in=observations)
                .exclude(current_chemo_protocol="")
                .values_list("current_chemo_protocol", flat=True)
                .distinct()
                .order_by("current_chemo_protocol")
            ),
            "outcomes": ["progressed", "deceased"],
        })


class AnalyticsSummaryAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_summary")
        cohort = self.get_cohort(request)
        observations = self.analysis_observations(request)
        rows = self.patient_rows(cohort, observations)
        treated = [row for row in rows if row["treatment"]]
        responded = [row for row in treated if row["response"]]
        return Response({"kpis": {
            "total_patients": len(rows),
            "observation_count": observations.count(),
            "new_diagnoses": sum(bool(row["diagnosis_date"]) for row in rows),
            "active_treatment": sum(row["active_treatment"] for row in rows),
            "recorded_response": len(responded),
            "response_rate": round(len(responded) / len(treated) * 100, 1) if treated else None,
            "pfs_available": sum(bool(row["treatment_start"] and row["last_follow_up"]) for row in rows),
            "os_available": sum(bool(row["diagnosis_date"] and row["last_follow_up"]) for row in rows),
        }, "definitions": self.definitions()})


class AnalyticsDistributionAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_distributions")
        rows = self.patient_rows(self.get_cohort(request), self.analysis_observations(request))
        completeness = [
            {"label": label, "count": sum(bool(row[key]) for row in rows), "total": len(rows)}
            for label, key in [("Diagnosis", "diagnosis"), ("Stage", "stage"), ("Pathology", "pathology"), ("Biomarker", "biomarker"), ("Treatment", "treatment"), ("Response", "response"), ("Diagnosis date", "diagnosis_date")]
        ]
        return Response({
            "stage": self.distribution(rows, "stage"),
            "histopathology": self.distribution(rows, "pathology"),
            "grade": self.distribution(rows, "grade"),
            "pathological_stage": self.distribution(rows, "pathological_stage"),
            "pathological_margin": self.distribution(rows, "pathological_margin"),
            "pathological_lvsi": self.distribution(rows, "pathological_lvsi"),
            "pathological_pni": self.distribution(rows, "pathological_pni"),
            "primary_site": self.distribution(rows, "primary_site"),
            "diagnosis_subgroup": self.distribution(rows, "diagnosis_subgroup"),
            "diagnosis_laterality": self.distribution(rows, "diagnosis_laterality"),
            "metastatic_site": self.distribution(rows, "metastatic_site"),
            "biomarker": self.distribution(rows, "biomarker"),
            "molecular_status": self.distribution(rows, "molecular_status"),
            "molecular_exon": self.distribution(rows, "molecular_exon"),
            "molecular_method": self.distribution(rows, "molecular_method"),
            "molecular_specimen": self.distribution(rows, "molecular_specimen"),
            "ihc_marker": self.distribution(rows, "ihc_marker"),
            "cancer_marker": self.distribution(rows, "cancer_marker"),
            "treatment": self.distribution(rows, "treatment"),
            "treatment_line": self.distribution(rows, "treatment_line"),
            "treatment_modality": self.distribution(rows, "treatment_modality"),
            "response": self.distribution(rows, "response"),
            "progression_status": self.distribution(rows, "progression_status"),
            "survival_status": self.distribution(rows, "survival_status"),
            "progression_site": self.distribution(rows, "progression_site"),
            "radiotherapy_intent": self.distribution(rows, "radiotherapy_intent"),
            "radiotherapy_site": self.distribution(rows, "radiotherapy_site"),
            "radiotherapy_modality": self.distribution(rows, "radiotherapy_modality"),
            "surgery_modality": self.distribution(rows, "surgery_modality"),
            "surgery_laterality": self.distribution(rows, "surgery_laterality"),
            "smoking_status": self.distribution(rows, "smoking_status"),
            "alcohol_history": self.distribution(rows, "alcohol_history"),
            "comorbidity": self.distribution(rows, "comorbidity"),
            "gender": self.distribution(rows, "gender"),
            "district": self.distribution(rows, "district"),
            "socio_economic_status": self.distribution(rows, "socio_economic_status"),
            "patient_type": self.distribution(rows, "patient_type"),
            "tb_status": self.distribution(rows, "tb_status"),
            "covid_status": self.distribution(rows, "covid_status"),
            "completeness": completeness,
        })


class AnalyticsFacetAPIView(AnalyticsQueryMixin, APIView):
    """Event-level drill-downs for clinical domains with meaningful dimensions."""

    permission_classes = [permissions.IsAuthenticated]

    SUBJECTS = {
        "histopathology": (Histopathology, "detail", {"method": "histology_type", "site": "site"}),
        "histopathology_method": (Histopathology, "histology_type", {"method": "histology_type", "site": "site"}),
        "histopathology_site": (Histopathology, "site", {"method": "histology_type", "site": "site"}),
        "molecular": (MolecularPathology, "status", {"method": "method", "gene": "gene"}),
        "molecular_gene": (MolecularPathology, "gene", {"method": "method", "gene": "gene"}),
        "molecular_method": (MolecularPathology, "method", {"method": "method", "gene": "gene"}),
        "molecular_specimen": (MolecularPathology, "specimen", {"method": "method", "gene": "gene"}),
        "molecular_exon": (MolecularPathology, "exon", {"method": "method", "gene": "gene"}),
        "cancer_marker": (CancerMarker, "name", {"unit": "unit"}),
        "cancer_marker_unit": (CancerMarker, "unit", {"unit": "unit"}),
        "treatment": (TreatmentCycle, "current_chemo_protocol", {"line": "line_of_treatment", "modality": "chemotherapy_modalities__detail"}),
        "treatment_line": (TreatmentCycle, "line_of_treatment", {"line": "line_of_treatment", "modality": "chemotherapy_modalities__detail"}),
        "treatment_modality": (TreatmentCycle, "chemotherapy_modalities__detail", {"line": "line_of_treatment", "modality": "chemotherapy_modalities__detail"}),
        "radiotherapy": (RadiotherapySchedule, "intent", {"site": "sites__value", "modality": "modalities__value"}),
        "radiotherapy_site": (RadiotherapySchedule, "sites__value", {"site": "sites__value", "modality": "modalities__value"}),
        "radiotherapy_modality": (RadiotherapySchedule, "modalities__value", {"site": "sites__value", "modality": "modalities__value"}),
        "surgery": (Surgery, "modality", {"laterality": "lateralities__value"}),
        "surgery_laterality": (Surgery, "lateralities__value", {"laterality": "lateralities__value"}),
    }

    def get(self, request):
        subject = request.query_params.get("subject", "")
        definition = self.SUBJECTS.get(subject)
        if not definition:
            return Response({"detail": "Unknown analytics subject."}, status=status.HTTP_400_BAD_REQUEST)
        model, measure, dimensions = definition
        count_mode = request.query_params.get("count_mode", "records")
        if count_mode not in {"records", "patients", "observations"}:
            return Response({"detail": "Unknown count mode."}, status=status.HTTP_400_BAD_REQUEST)
        self.audit(request, f"analytics_facet_{subject}")
        base = model.objects.filter(
            observation__in=self.analysis_observations(request),
        )
        queryset = base
        for parameter, lookup in dimensions.items():
            value = (request.query_params.get(parameter) or "").strip()
            if value:
                queryset = queryset.filter(**{lookup: value})
        items = list(
            queryset.exclude(**{measure: ""})
            .values(measure)
            .annotate(count=Count(
                {"records": "id", "patients": "observation__patient_id", "observations": "observation_id"}[count_mode],
                distinct=True,
            ))
            .order_by("-count", measure)
        )
        return Response({
            "subject": subject,
            "measure": measure,
            "count_mode": count_mode,
            "unit": {"records": "clinical records", "patients": "patients", "observations": "test events"}[count_mode],
            "items": [{"label": item[measure], "count": item["count"]} for item in items],
            "filters": {
                parameter: list(
                    base.exclude(**{lookup: ""}).values_list(lookup, flat=True).distinct().order_by(lookup)
                )
                for parameter, lookup in dimensions.items()
            },
        })


class AnalyticsMolecularSummaryAPIView(AnalyticsQueryMixin, APIView):
    """Clearly separated patient, test-event, and result-entry measures for molecular data."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_molecular_summary")
        records = MolecularPathology.objects.filter(observation__in=self.analysis_observations(request))
        for parameter in ("method", "gene"):
            value = (request.query_params.get(parameter) or "").strip()
            if value:
                records = records.filter(**{parameter: value})
        return Response({
            "patients_tested": records.values("observation__patient_id").distinct().count(),
            "test_events": records.values("observation_id").distinct().count(),
            "result_entries": records.count(),
            "methods_recorded": records.exclude(method="").values("method").distinct().count(),
            "definition": "A test event is one published clinical observation with molecular data. A result entry is one gene-level molecular record; one test event may contain several result entries.",
        })


class AnalyticsMolecularChronologyAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_molecular_chronology")
        count_mode = request.query_params.get("count_mode", "events")
        if count_mode not in {"patients", "events", "entries"}:
            return Response({"detail": "Unknown count mode."}, status=status.HTTP_400_BAD_REQUEST)
        records = MolecularPathology.objects.filter(observation__in=self.analysis_observations(request)).select_related("observation")
        for parameter in ("method", "gene"):
            value = (request.query_params.get(parameter) or "").strip()
            if value:
                records = records.filter(**{parameter: value})

        buckets = {}
        for record in records:
            event_date = record.observed_on or (record.observation.observed_at.date() if record.observation.observed_at else None)
            if not event_date:
                continue
            bucket = event_date.strftime("%Y-%m")
            buckets.setdefault(bucket, {"entries": 0, "events": set(), "patients": set()})
            buckets[bucket]["entries"] += 1
            buckets[bucket]["events"].add(record.observation_id)
            buckets[bucket]["patients"].add(record.observation.patient_id)
        return Response({
            "count_mode": count_mode,
            "unit": {"patients": "patients", "events": "test events", "entries": "result entries"}[count_mode],
            "items": [
                {"label": label, "count": value["entries"] if count_mode == "entries" else len(value[count_mode])}
                for label, value in sorted(buckets.items())
            ],
        })


class AnalyticsMolecularResultBreakdownAPIView(AnalyticsQueryMixin, APIView):
    """Method × gene × result cross-tab; the directly interpretable molecular view."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_molecular_result_breakdown")
        count_mode = request.query_params.get("count_mode", "entries")
        if count_mode not in {"patients", "events", "entries"}:
            return Response({"detail": "Unknown count mode."}, status=status.HTTP_400_BAD_REQUEST)
        records = MolecularPathology.objects.filter(observation__in=self.analysis_observations(request))
        for parameter in ("method", "gene"):
            value = (request.query_params.get(parameter) or "").strip()
            if value:
                records = records.filter(**{parameter: value})
        count_field = {"patients": "observation__patient_id", "events": "observation_id", "entries": "id"}[count_mode]
        rows = list(
            records.exclude(method="").exclude(gene="").exclude(status="")
            .values("method", "gene", "status")
            .annotate(count=Count(count_field, distinct=True))
            .order_by("method", "gene", "status")
        )
        return Response({
            "count_mode": count_mode,
            "unit": {"patients": "patients", "events": "test events", "entries": "result entries"}[count_mode],
            "statuses": sorted({row["status"] for row in rows}),
            "rows": rows,
        })


class AnalyticsPatientMatchesAPIView(AnalyticsQueryMixin, APIView):
    """Patient-level traceability for the active analytics cohort or domain."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subject = request.query_params.get("subject", "").strip()
        self.audit(request, f"analytics_patient_matches_{subject or 'cohort'}")

        if subject:
            definition = AnalyticsFacetAPIView.SUBJECTS.get(subject)
            if not definition:
                return Response({"detail": "Unknown analytics subject."}, status=status.HTTP_400_BAD_REQUEST)
            model, _, dimensions = definition
            records = model.objects.filter(observation__in=self.analysis_observations(request))
            for parameter, lookup in dimensions.items():
                value = (request.query_params.get(parameter) or "").strip()
                if value:
                    records = records.filter(**{lookup: value})
            rows = records.values(
                "observation__patient_id",
                "observation__patient__registry_id",
                "observation__patient__name",
                "observation__patient__registration_no",
                "observation__patient__phone",
                "observation__patient__email",
                "observation__patient__age",
                "observation__patient__gender",
                "observation__patient__district",
            ).annotate(
                matching_records=Count("id", distinct=True),
                latest_observation=Max("observation__observed_at"),
            ).order_by("observation__patient__registry_id")
            scope = "Matching domain records across the included patients' published journeys."
        else:
            rows = self.matching_observations(request).values(
                "patient_id",
                "patient__registry_id",
                "patient__name",
                "patient__registration_no",
                "patient__phone",
                "patient__email",
                "patient__age",
                "patient__gender",
                "patient__district",
            ).annotate(
                matching_records=Count("id", distinct=True),
                latest_observation=Max("observed_at"),
            ).order_by("patient__registry_id")
            scope = "Published clinical observations that match the global cohort filters."

        rows = list(rows)
        patient_ids = [row.get("observation__patient_id", row.get("patient_id")) for row in rows]
        clinical_rows = {
            row["patient"].id: row
            for row in self.patient_rows(
                Patient.objects.filter(id__in=patient_ids, deleted_at__isnull=True),
                self.analysis_observations(request),
            )
        }
        detail_keys = (
            "diagnosis", "primary_site", "diagnosis_subgroup", "diagnosis_laterality", "stage",
            "pathological_stage", "pathology", "grade", "metastatic_site", "biomarker",
            "molecular_status", "molecular_exon", "molecular_method", "molecular_specimen",
            "cancer_marker", "treatment", "treatment_line", "treatment_modality", "response",
            "progression_status", "survival_status", "radiotherapy_intent", "radiotherapy_site",
            "radiotherapy_modality", "surgery_modality", "surgery_laterality", "smoking_status",
            "comorbidity", "diagnosis_date", "treatment_start", "progression_date", "death_date",
            "last_follow_up",
        )
        items = []
        for row in rows:
            patient_id = row.get("observation__patient_id", row.get("patient_id"))
            prefix = "observation__patient__" if subject else "patient__"
            clinical = clinical_rows.get(patient_id, {})
            molecular_methods = "; ".join(sorted({
                item.method for record in clinical.get("records", [])
                for item in record.molecular_pathologies.all() if item.method
            }))
            items.append({
                "registry_id": row[f"{prefix}registry_id"],
                "name": row[f"{prefix}name"],
                "registration_no": row[f"{prefix}registration_no"],
                "phone": row[f"{prefix}phone"],
                "email": row[f"{prefix}email"],
                "age": row[f"{prefix}age"],
                "gender": row[f"{prefix}gender"],
                "district": row[f"{prefix}district"],
                "matching_records": row["matching_records"],
                "latest_observation": row["latest_observation"],
                "molecular_methods": molecular_methods,
                **{key: clinical.get(key) for key in detail_keys},
            })
        return Response({"subject": subject or "cohort", "scope": scope, "count": len(items), "items": items})


class AnalyticsSurvivalAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_survival")
        rows = self.patient_rows(self.get_cohort(request), self.analysis_observations(request))
        result = []
        for metric, start_key, event_key in (("pfs", "treatment_start", "progression_date"), ("os", "diagnosis_date", "death_date")):
            values = []
            for row in rows:
                start = row[start_key]
                end = row[event_key] or row["last_follow_up"]
                if start and end and end >= start:
                    values.append((end - start).days)
            result.append({"metric": metric, "available": len(values), "median_days": median(values) if values else None, "values": values})
        return Response({"survival": result, "definitions": self.definitions()})


class AnalyticsExportAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_export")
        rows = self.patient_rows(self.get_cohort(request), self.analysis_observations(request))
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="analytics_cohort_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Registry ID", "Patient", "Registration no.", "Age", "Gender", "District", "Diagnosis", "Primary site", "Stage", "Pathological stage", "Pathology", "Grade",
            "Metastatic site", "Biomarker", "Molecular method (latest)", "Molecular methods (all)", "Molecular status", "Molecular exon", "Molecular specimen", "IHC marker", "Treatment", "Treatment line",
            "Treatment modality", "Radiotherapy intent", "Radiotherapy site", "Radiotherapy modality",
            "Surgery modality", "Smoking status", "Comorbidity", "Response", "Progression status",
            "Survival status", "Diagnosis date", "Treatment start", "Progression date", "Death date", "Last follow-up",
        ])
        for row in rows:
            writer.writerow([
                row["patient"].registry_id, row["patient"].name, row["patient"].registration_no, row["patient"].age, row["patient"].gender, row["patient"].district, row["diagnosis"], row["primary_site"], row["stage"], row["pathological_stage"], row["pathology"], row["grade"],
                row["metastatic_site"], row["biomarker"], row["molecular_method"], "; ".join(sorted({item.method for record in row["records"] for item in record.molecular_pathologies.all() if item.method})), row["molecular_status"], row["molecular_exon"], row["molecular_specimen"], row["ihc_marker"], row["treatment"], row["treatment_line"],
                row["treatment_modality"], row["radiotherapy_intent"], row["radiotherapy_site"], row["radiotherapy_modality"],
                row["surgery_modality"], row["smoking_status"], row["comorbidity"], row["response"], row["progression_status"],
                row["survival_status"], row["diagnosis_date"], row["treatment_start"], row["progression_date"], row["death_date"], row["last_follow_up"],
            ])
        return response


class CsrfCookieAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detail": "CSRF cookie set."})


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        requested_role = (request.data.get("role") or "user").strip().lower()
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if requested_role not in {"admin", "doctor", "user"}:
            return Response(
                {"detail": "Invalid role selection."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user_has_role(user, requested_role):
            return Response(
                {"detail": f"This account does not have {requested_role} access."},
                status=status.HTTP_403_FORBIDDEN,
            )
        login(request, user)
        return Response({"user": serialize_user(user), "requested_role": requested_role})


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"user": serialize_user(request.user)})


class PatientDemographicsLookupAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        district = (request.GET.get("district") or "").strip()
        response = {
            "genders": list(GenderOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)),
            "blood_groups": list(
                BloodGroupOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "districts": list(
                DistrictOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "police_stations": list(
                PoliceStationOption.objects.filter(
                    is_active=True,
                    district__name=district,
                )
                .order_by("name")
                .values_list("name", flat=True)
                if district
                else []
            ),
            "socio_economic_statuses": list(
                SocioEconomicStatusOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "patient_types": list(
                PatientTypeOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "marital_statuses": list(
                MaritalStatusOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "alcohol_history_options": list(
                AlcoholHistoryOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "smoking_statuses": list(
                SmokingStatusOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "tb_statuses": list(
                TuberculosisStatusOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "covid_statuses": list(
                CovidStatusOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "covid_vaccine_names": list(
                CovidVaccineOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "covid_vaccination_doses": list(
                CovidVaccinationDoseOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "diagnosis_disease_groups": list(
                DiagnosisDiseaseGroupOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "diagnosis_disease_subgroups": list(
                DiagnosisDiseaseSubgroupOption.objects.filter(
                    is_active=True,
                    group__name=(request.GET.get("disease_group") or "").strip(),
                )
                .order_by("name")
                .values_list("name", flat=True)
                if (request.GET.get("disease_group") or "").strip()
                else []
            ),
            "diagnosis_primary_sites": list(
                DiagnosisPrimarySiteOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "diagnosis_lateralities": list(
                DiagnosisLateralityOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "diagnosis_metastatic_sites": list(
                DiagnosisMetastaticSiteOption.objects.filter(is_active=True)
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "histopathology_details": list(
                HistopathologyOption.objects.filter(is_active=True, category="detail")
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "histopathology_types": list(
                HistopathologyOption.objects.filter(is_active=True, category="type")
                .order_by("name")
                .values_list("name", flat=True)
            ),
            "ihc_marker_types": list(
                IhcMarkerOption.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            ),
            "molecular_pathology_options": {
                group_name: list(
                    MolecularPathologyOption.objects.filter(is_active=True, group=group_name)
                    .order_by("name")
                    .values_list("name", flat=True)
                )
                for group_name in MolecularPathologyOption.objects.filter(is_active=True)
                .order_by("group")
                .values_list("group", flat=True)
                .distinct()
            },
        }
        return Response(response)


class PatientCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PatientEntrySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        return Response(
            {
                "id": patient.id,
                "registry_id": patient.registry_id,
                "name": patient.name,
            },
            status=status.HTTP_201_CREATED,
        )


class LegacyUnlinkedHistoryAPIView(APIView):
    """Admin-only review queue for legacy history chains without an observation parent."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not user_is_admin(request.user):
            return Response(
                {"detail": "Only registry administrators can review legacy import anomalies."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            page = max(int(request.GET.get("page", 1)), 1)
            per_page = min(max(int(request.GET.get("per_page", 25)), 1), 100)
        except ValueError:
            return Response({"detail": "page and per_page must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        resolution_status = (request.GET.get("status") or "open").strip().lower()
        if resolution_status not in dict(LegacyImportAnomaly.ResolutionStatus.choices):
            return Response({"detail": "Invalid anomaly status."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = LegacyImportAnomaly.objects.filter(
            source_table="patient_histories",
            resolution_status=resolution_status,
        ).order_by("missing_reference_id", "legacy_row_id")
        query = (request.GET.get("q") or "").strip()
        if query:
            try:
                legacy_id = int(query)
            except ValueError:
                queryset = queryset.none()
            else:
                queryset = queryset.filter(
                    Q(legacy_row_id=legacy_id) | Q(missing_reference_id=legacy_id)
                )

        count = queryset.count()
        start = (page - 1) * per_page
        anomalies = queryset[start : start + per_page]
        results = []
        for anomaly in anomalies:
            payload = anomaly.payload or {}
            results.append(
                {
                    "legacy_history_id": anomaly.legacy_row_id,
                    "missing_observation_id": anomaly.missing_reference_id,
                    "marital_status": payload.get("marital_status") or "",
                    "first_diagnosis_date": payload.get("first_diagnosis_date"),
                    "created_at": payload.get("created_at"),
                    "updated_at": payload.get("updated_at"),
                    "resolution_status": anomaly.resolution_status,
                }
            )

        return Response(
            {
                "count": count,
                "page": page,
                "per_page": per_page,
                "next": page + 1 if start + per_page < count else None,
                "previous": page - 1 if page > 1 else None,
                "results": results,
            }
        )
