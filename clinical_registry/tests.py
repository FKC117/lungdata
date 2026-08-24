from django.contrib.auth import get_user_model
from django.test import TestCase

from clinical_registry.models import LegacyImportAnomaly
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
