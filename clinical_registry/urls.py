from django.urls import path

from clinical_registry.views import (
    CsrfCookieAPIView,
    CurrentUserAPIView,
    DashboardSummaryAPIView,
    LoginAPIView,
    LegacyUnlinkedHistoryAPIView,
    LogoutAPIView,
    PatientDemographicsLookupAPIView,
    PatientCreateAPIView,
    PatientDetailAPIView,
    PatientExportAPIView,
    PatientListAPIView,
    PatientUpdateAPIView,
    AnalyticsDistributionAPIView,
    AnalyticsExportAPIView,
    AnalyticsFiltersAPIView,
    AnalyticsSummaryAPIView,
    AnalyticsSurvivalAPIView,
)


urlpatterns = [
    path("auth/csrf/", CsrfCookieAPIView.as_view(), name="auth-csrf"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="auth-me"),
    path("patients/demographics/", PatientDemographicsLookupAPIView.as_view(), name="patient-demographics"),
    path("patients/create/", PatientCreateAPIView.as_view(), name="patient-create"),
    path("patients/<str:registry_id>/update/", PatientUpdateAPIView.as_view(), name="patient-update"),
    path("dashboard/summary/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("analytics/filters/", AnalyticsFiltersAPIView.as_view(), name="analytics-filters"),
    path("analytics/summary/", AnalyticsSummaryAPIView.as_view(), name="analytics-summary"),
    path("analytics/distributions/", AnalyticsDistributionAPIView.as_view(), name="analytics-distributions"),
    path("analytics/survival/", AnalyticsSurvivalAPIView.as_view(), name="analytics-survival"),
    path("analytics/export/", AnalyticsExportAPIView.as_view(), name="analytics-export"),
    path("legacy-review/unlinked-histories/", LegacyUnlinkedHistoryAPIView.as_view(), name="legacy-unlinked-histories"),
    path("patients/export/", PatientExportAPIView.as_view(), name="patient-export"),
    path("patients/", PatientListAPIView.as_view(), name="patient-list"),
    path("patients/<str:registry_id>/", PatientDetailAPIView.as_view(), name="patient-detail"),
]
