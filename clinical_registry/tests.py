from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from clinical_registry.models import (
    AnalyticsAuditEvent,
    ClinicalObservation,
    ClinicalStaging,
    LegacyImportAnomaly,
    MolecularPathology,
    Patient,
    PatientHistory,
    TreatmentCycle,
)
from clinical_registry.serializers import PatientEntrySerializer


class PatientEntryLegacyFieldCompatibilityTests(TestCase):
    def test_react_aliases_are_saved_to_legacy_history_and_observation_columns(self):
        serializer = PatientEntrySerializer(
            data={
                "name": "Compatibility Test Patient",
                "observed_at": "2026-08-23T10:00:00Z",
                "diagnosis_laterality": "Left",
                "laterality_notes": "Left lung",
                "history": {
                    "height_cm": "165.00",
                    "weight_kg": "60.00",
                    "alcohol_history": "No",
                    "radiotherapy_to_chest": "No",
                    "family_cancer_history": "None",
                },
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        patient = serializer.save()
        observation = patient.observations.get()
        history = observation.history

        self.assertEqual(observation.time, observation.observed_at)
        self.assertEqual(observation.diagnosis_laterility, "Left")
        self.assertEqual(observation.laterality, "Left lung")
        self.assertEqual(history.height, history.height_cm)
        self.assertEqual(history.weight, history.weight_kg)
        self.assertEqual(history.h_o_alcoholism, history.alcohol_history)
        self.assertEqual(history.rt_to_chest, history.radiotherapy_to_chest)
        self.assertEqual(history.cancer_history, history.family_cancer_history)


class LegacyReviewAccessTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="registry-admin",
            email="registry-admin@example.com",
            password="safe-test-password",
        )
        self.user = get_user_model().objects.create_user(
            username="standard-user",
            password="safe-test-password",
        )
        LegacyImportAnomaly.objects.create(
            source_table="patient_histories",
            legacy_row_id=8,
            missing_reference_field="patient_observation_id",
            missing_reference_id=8,
            reason="missing patient_observation_id 8",
            payload={"marital_status": "Married"},
        )

    def test_only_admin_can_view_unlinked_history_review_queue(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/api/legacy-review/unlinked-histories/").status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.get("/api/legacy-review/unlinked-histories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["missing_observation_id"], 8)


class AnalyticsReadOnlyTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="analytics-admin", email="analytics@example.com", password="safe-test-password"
        )
        self.patient = Patient.objects.create(name="DUMMY-1", registry_id="DUMMY-1")
        self.observation = ClinicalObservation.objects.create(
            patient=self.patient,
            observed_at=timezone.now(),
            diagnosis_disease_group="NSCLC",
            is_draft=False,
        )
        PatientHistory.objects.create(observation=self.observation, first_diagnosis_date="2026-01-01")
        ClinicalStaging.objects.create(observation=self.observation, result="Stage IV")
        MolecularPathology.objects.create(observation=self.observation, gene="EGFR", status="Positive")
        TreatmentCycle.objects.create(
            observation=self.observation,
            current_chemo_protocol="Osimertinib",
            chemo_starting_date="2026-01-10",
            recist_1_result="PR",
        )
        draft_patient = Patient.objects.create(name="Draft only", registry_id="DRAFT-1")
        ClinicalObservation.objects.create(patient=draft_patient, observed_at=timezone.now(), is_draft=True)

    def test_summary_uses_published_patient_cohort_and_audits_access(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/analytics/summary/?diagnosis=NSCLC")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["kpis"]["total_patients"], 1)
        self.assertEqual(response.json()["kpis"]["recorded_response"], 1)
        self.assertEqual(AnalyticsAuditEvent.objects.filter(action="analytics_summary").count(), 1)
