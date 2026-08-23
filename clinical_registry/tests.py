from django.test import TestCase

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
