import csv
from collections import Counter
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import BooleanField, CharField, Count, Min, OuterRef, Prefetch, Q, Subquery
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
    Histopathology,
    MolecularPathology,
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

    def get_cohort(self, request):
        observations = scope_observations_for_user(
            ClinicalObservation.objects.filter(deleted_at__isnull=True, is_draft=False),
            request.user,
        )
        params = request.query_params
        start, end = params.get("start_date"), params.get("end_date")
        if start:
            observations = observations.filter(observed_at__date__gte=start)
        if end:
            observations = observations.filter(observed_at__date__lte=end)
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
            observations = observations.filter(treatment_cycles__current_chemo_protocol__icontains=params["treatment"])
        if params.get("outcome") == "progressed":
            observations = observations.filter(treatment_cycles__disease_progression_status__icontains="progress")
        elif params.get("outcome") == "deceased":
            observations = observations.filter(treatment_cycles__survival_status__icontains="dead")
        patient_ids = observations.values_list("patient_id", flat=True).distinct()
        return Patient.objects.filter(id__in=patient_ids, deleted_at__isnull=True).distinct()

    @staticmethod
    def latest_nonblank(items, attribute):
        values = [getattr(item, attribute) for item in items if getattr(item, attribute, None)]
        return values[-1] if values else ""

    def patient_rows(self, cohort):
        observations = ClinicalObservation.objects.filter(
            patient__in=cohort, deleted_at__isnull=True, is_draft=False
        ).select_related("center", "doctor").prefetch_related(
            "history", "clinical_stagings", "histopathologies", "molecular_pathologies", "treatment_cycles"
        ).order_by("patient_id", "observed_at", "id")
        grouped = {}
        for observation in observations:
            grouped.setdefault(observation.patient_id, []).append(observation)
        rows = []
        for patient in cohort:
            records = grouped.get(patient.id, [])
            stages = [stage for record in records for stage in record.clinical_stagings.all()]
            molecular = [item for record in records for item in record.molecular_pathologies.all()]
            cycles = [item for record in records for item in record.treatment_cycles.all()]
            histories = [record.history for record in records if hasattr(record, "history")]
            diagnosis_date = min((item.first_diagnosis_date for item in histories if item.first_diagnosis_date), default=None)
            treatment_start = min((item.chemo_starting_date for item in cycles if item.chemo_starting_date), default=None)
            progression_dates = [item.disease_progression_status_date for item in cycles if item.disease_progression_status_date]
            death_dates = [item.survival_status_date for item in cycles if item.survival_status_date and "dead" in item.survival_status.lower()]
            last_follow_up = max((item.observed_at.date() for item in records if item.observed_at), default=None)
            response = self.latest_nonblank(cycles, "recist_1_result") or self.latest_nonblank(cycles, "irecist_result")
            rows.append({
                "patient": patient, "records": records,
                "diagnosis": self.latest_nonblank(records, "diagnosis_disease_group"),
                "stage": self.latest_nonblank(stages, "result"),
                "pathology": self.latest_nonblank([x for r in records for x in r.histopathologies.all()], "histology_type"),
                "biomarker": self.latest_nonblank(molecular, "gene"),
                "treatment": self.latest_nonblank(cycles, "current_chemo_protocol"),
                "response": response, "diagnosis_date": diagnosis_date,
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
            "date_range": "Filters on published clinical-observation date, inclusive.",
            "response_rate": "Patients with a recorded RECIST 1.1 or iRECIST result divided by patients with a treatment record.",
            "pfs": "Days from first chemotherapy start to recorded progression or death; censored at last published observation when neither is recorded.",
            "os": "Days from first diagnosis to recorded death; censored at last published observation when death is not recorded.",
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
            "treatments": list(TreatmentCycle.objects.filter(observation__in=observations).exclude(current_chemo_protocol="").values_list("current_chemo_protocol", flat=True).distinct().order_by("current_chemo_protocol")),
            "outcomes": ["progressed", "deceased"],
        })


class AnalyticsSummaryAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_summary")
        rows = self.patient_rows(self.get_cohort(request))
        treated = [row for row in rows if row["treatment"]]
        responded = [row for row in treated if row["response"]]
        return Response({"kpis": {
            "total_patients": len(rows),
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
        rows = self.patient_rows(self.get_cohort(request))
        completeness = [
            {"label": label, "count": sum(bool(row[key]) for row in rows), "total": len(rows)}
            for label, key in [("Diagnosis", "diagnosis"), ("Stage", "stage"), ("Pathology", "pathology"), ("Biomarker", "biomarker"), ("Treatment", "treatment"), ("Response", "response"), ("Diagnosis date", "diagnosis_date")]
        ]
        return Response({"stage": self.distribution(rows, "stage"), "biomarker": self.distribution(rows, "biomarker"), "treatment": self.distribution(rows, "treatment"), "response": self.distribution(rows, "response"), "completeness": completeness})


class AnalyticsSurvivalAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_survival")
        rows = self.patient_rows(self.get_cohort(request))
        result = []
        for metric, start_key, event_key in (("pfs", "treatment_start", "progression_date"), ("os", "diagnosis_date", "death_date")):
            values = []
            for row in rows:
                start = row[start_key]
                end = row[event_key] or row["last_follow_up"]
                if start and end and end >= start:
                    values.append((end - start).days)
            result.append({"metric": metric, "available": len(values), "median_days": sorted(values)[len(values) // 2] if values else None, "values": values})
        return Response({"survival": result, "definitions": self.definitions()})


class AnalyticsExportAPIView(AnalyticsQueryMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        self.audit(request, "analytics_export")
        rows = self.patient_rows(self.get_cohort(request))
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="analytics_cohort_export.csv"'
        writer = csv.writer(response)
        writer.writerow(["Registry ID", "Diagnosis", "Stage", "Pathology", "Biomarker", "Treatment", "Response", "Diagnosis date", "Treatment start", "Progression date", "Death date", "Last follow-up"])
        for row in rows:
            writer.writerow([row["patient"].registry_id, row["diagnosis"], row["stage"], row["pathology"], row["biomarker"], row["treatment"], row["response"], row["diagnosis_date"], row["treatment_start"], row["progression_date"], row["death_date"], row["last_follow_up"]])
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
