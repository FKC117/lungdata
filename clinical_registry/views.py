import csv

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import BooleanField, CharField, Count, OuterRef, Prefetch, Q, Subquery
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clinical_registry.models import (
    AlcoholHistoryOption,
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
    DistrictOption,
    GenderOption,
    HistopathologyOption,
    IhcMarkerOption,
    MaritalStatusOption,
    MolecularPathologyOption,
    Patient,
    PatientTypeOption,
    PoliceStationOption,
    SmokingStatusOption,
    SocioEconomicStatusOption,
    TuberculosisStatusOption,
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
    if user_is_in_named_group(user, "Doctor", "Doctors"):
        return "doctor"
    return "user"


def get_default_redirect_for_role(role):
    if role == "admin":
        return "/admin/"
    return "/patients"


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
    return {
        "id": user.id,
        "username": user.get_username(),
        "full_name": user.get_full_name() or user.get_username(),
        "email": user.email,
        "role": role,
        "default_redirect": get_default_redirect_for_role(role),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }


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
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        for patient in queryset:
            patient.prefetched_latest_observation = (
                patient.prefetched_observations[0] if getattr(patient, "prefetched_observations", []) else None
            )
        serializer = self.get_serializer(queryset, many=True)
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
                "treatment_cycles",
                "radiotherapy_schedules__sites",
                "radiotherapy_schedules__modalities",
                "surgeries__lateralities",
            )
            .order_by("-observed_at", "-id")
        )
        return Patient.objects.filter(deleted_at__isnull=True).prefetch_related(
            Prefetch("observations", queryset=observation_queryset)
        )


class DashboardSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = {
            "patients": Patient.objects.filter(deleted_at__isnull=True).count(),
            "observations": ClinicalObservation.objects.filter(deleted_at__isnull=True).count(),
            "published_patients": Patient.objects.filter(
                deleted_at__isnull=True,
                observations__is_draft=False,
            ).distinct().count(),
            "draft_patients": Patient.objects.filter(
                deleted_at__isnull=True,
                observations__is_draft=True,
            ).distinct().count(),
            "published_observations": ClinicalObservation.objects.filter(
                deleted_at__isnull=True,
                is_draft=False,
            ).count(),
            "draft_observations": ClinicalObservation.objects.filter(
                deleted_at__isnull=True,
                is_draft=True,
            ).count(),
        }
        return Response(data)


class CsrfCookieAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @ensure_csrf_cookie
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
        serializer = PatientEntrySerializer(data=request.data)
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
