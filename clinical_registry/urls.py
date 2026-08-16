from django.urls import path

from clinical_registry.views import (
    CsrfCookieAPIView,
    CurrentUserAPIView,
    DashboardSummaryAPIView,
    LoginAPIView,
    LogoutAPIView,
    PatientDemographicsLookupAPIView,
    PatientCreateAPIView,
    PatientDetailAPIView,
    PatientExportAPIView,
    PatientListAPIView,
    PatientUpdateAPIView,
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
    path("patients/export/", PatientExportAPIView.as_view(), name="patient-export"),
    path("patients/", PatientListAPIView.as_view(), name="patient-list"),
    path("patients/<str:registry_id>/", PatientDetailAPIView.as_view(), name="patient-detail"),
]
