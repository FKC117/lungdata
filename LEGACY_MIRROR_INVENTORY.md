# Legacy Mirror Inventory

Date: August 16, 2026

## Purpose
This document classifies the current backend against the legacy schema so we can migrate safely without breaking live data compatibility.

Legend:

- `KEEP`: current Django model is already a usable mirror base
- `RENAME/REMODEL`: current model exists but field naming or relationships should be brought closer to legacy
- `ADD MIRROR MODEL`: legacy table exists but needs a dedicated mirrored Django model

## Core Clinical Tables

| Legacy table | Current Django status | Action | Notes |
| --- | --- | --- | --- |
| `patients` | `Patient` exists | `KEEP` | Legacy table name is now mirrored and key legacy fields like `photo` are present. `created_by` remains an app-layer helper field. |
| `patient_observations` | `ClinicalObservation` exists | `RENAME/REMODEL` | Legacy table name is mirrored and key fields are present; remaining drift is helper fields like `consulting_doctor_name`, `center_name`, and duplicate normalized aliases beside legacy names. |
| `patient_histories` | `PatientHistory` exists | `RENAME/REMODEL` | Legacy table name is mirrored and key legacy fields are present; remaining drift is duplicate normalized aliases beside legacy names. |
| `patient_observation_details` | `TreatmentCycle` exists | `KEEP` | Already a close semantic mirror of the treatment detail table. |
| `smoking_histories` | `SmokingHistory` exists | `KEEP` | Good mirror base. |
| `tb_histories` | `TuberculosisHistory` exists | `KEEP` | Good mirror base. |
| `covid_histories` | `CovidHistory` exists | `KEEP` | Good mirror base. |
| `diagnoses` | `Diagnosis` exists | `KEEP` | Good mirror base. |
| `diagnosis_metastatic_sites` | `DiagnosisMetastaticSite` exists | `KEEP` | Good mirror base. |
| `comorbidities` | `Comorbidity` exists | `KEEP` | Good mirror base. |
| `histopathologies` | `Histopathology` exists | `KEEP` | Good mirror base. |
| `molecular_pathologies` | `MolecularPathology` exists | `KEEP` | Good mirror base. |
| `cancer_markers` | `CancerMarker` exists | `KEEP` | Good mirror base. |
| `staging_clinicals` | `ClinicalStaging` exists | `KEEP` | Good mirror base. |
| `staging_pathologicals` | `PathologicalStaging` exists | `KEEP` | Good mirror base. |
| `staging_pathological_details` | `PathologicalStagingDetail` exists | `KEEP` | Good mirror base. |
| `ihcs` | `Immunohistochemistry` exists | `KEEP` | Good mirror base. |
| `ihc_details` | `IHCDetail` exists | `KEEP` | Good mirror base. |
| `past_treatment_histories` | `PastTreatmentHistory` exists | `KEEP` | Good mirror base. |
| `radiotherapy_schedules` | `RadiotherapySchedule` exists | `KEEP` | Good mirror base. |
| `radiotherapy_schedule_sites` | `RadiotherapyScheduleSite` exists | `KEEP` | Good mirror base. |
| `radiotherapy_schedule_modalities` | `RadiotherapyScheduleModality` exists | `KEEP` | Good mirror base. |
| `surgeries` | `Surgery` exists | `KEEP` | Good mirror base. |
| `surgical_lateralities` | `SurgicalLaterality` exists | `KEEP` | Good mirror base. |
| `chemotherapy_protocols` | `ChemotherapyProtocol` exists | `KEEP` | Good mirror base. |
| `chemotherapy_protocol_details` | `ChemotherapyProtocolDetail` exists | `KEEP` | Good mirror base. |
| `chemotherapy_modalities` | `ChemotherapyModality` exists | `KEEP` | Good mirror base. |
| `patient_observation_response_rate_progression_sites` | `TreatmentCycleProgressionSite` exists | `KEEP` | Good mirror base. |

## Doctor And Center Layer

| Legacy table | Current Django status | Action | Notes |
| --- | --- | --- | --- |
| `centers` | `Center` added | `ADD MIRROR MODEL` | Implemented as first mirror pass. |
| `doctors` | `Doctor` added | `ADD MIRROR MODEL` | Implemented as first mirror pass. |
| `doctor_degrees` | `DoctorDegree` added | `ADD MIRROR MODEL` | Implemented as first mirror pass. |
| `doctor_patients` | `DoctorPatient` added | `ADD MIRROR MODEL` | Implemented as first mirror pass. |
| `doctor_recognition_records` | `DoctorRecognitionRecord` added | `ADD MIRROR MODEL` | Implemented as first mirror pass. |
| `DoctorProfile` | app-layer only | `RENAME/REMODEL` | Keep as helper only; now supports explicit linkage to mirrored legacy `Doctor` for access control. |

## Legacy Reference / Record Tables

| Legacy table | Current Django status | Action | Notes |
| --- | --- | --- | --- |
| `diagnosis_disease_group_records` | canonical option model only | `ADD MIRROR MODEL` | Current option model is not a strict mirror. |
| `diagnosis_disease_subgroup_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `diagnosis_primary_site_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `diagnosis_laterility_records` | canonical option model only | `ADD MIRROR MODEL` | Must preserve legacy spelling. |
| `diagnosis_metastatic_site_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `histopathology_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `ihc_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `molecular_pathology_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `cancer_marker_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `chemotherapy_protocol_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `chemotherapy_modality_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `radiotherapy_schedule_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `radiotherapy_schedule_intent_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `surgery_modality_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `surgical_laterality_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `socio_economic_status_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `survival_status_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `disease_progression_status_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `line_of_treatment_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `response_rate_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `response_rate_calculation_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `staging_calculation_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `covid_vaccine_company_records` | canonical option model only | `ADD MIRROR MODEL` | Needs exact mirrored table. |
| `comorbidity_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |
| `exon_records` | no mirror yet | `ADD MIRROR MODEL` | Missing. |

## Auth / System Tables

| Legacy table | Current Django status | Action | Notes |
| --- | --- | --- | --- |
| `users` | `LegacyUser` added | `ADD MIRROR MODEL` | Passive mirror only; preserved for provenance and audit, not used for Django authentication. |
| `auth_user` and auth tables | Django native | `KEEP` | New Django auth layer. |

## Current Safe Rule

1. Clinical tables that already mirror legacy reasonably well should stay.
2. Doctor / center / lookup-record truth should move toward exact legacy mirror models.
3. App-layer permissions should prefer mirrored doctor relations first and use invented ownership only as a fallback for newly created local records.

## Safe Doctor Link Workflow

Use this when a Django-auth doctor account must be tied to a mirrored legacy doctor record for permissions and visibility.

1. Review suggestions without changing data:
   `python manage.py suggest_doctor_profile_links`
2. If a match is correct, verify it once more in Django admin:
   `Auth > Users > doctor profile`
   `Clinical Registry > Doctors`
3. Dry-run the explicit link:
   `python manage.py link_doctor_profile <doctor_profile_id> <doctor_id> --dry-run`
4. Apply the explicit link only after verification:
   `python manage.py link_doctor_profile <doctor_profile_id> <doctor_id>`

This workflow is intentionally manual. We do not auto-link users to legacy doctors during import or login.

## Remaining Mirror Gaps

1. `patient_observations`
   Keep the mirrored table name, but gradually remove helper-only duplicate aliases once every API serializer and React form is reading the legacy-style fields directly.
2. `patient_histories`
   Same cleanup path as `patient_observations`: preserve the mirrored table and legacy fields, then retire duplicate normalized aliases after API parity is complete.
3. Unpublished or pre-observation chains
   The local import now audits unresolved rows into `LegacyImportAnomaly`, but those rows are not yet loaded into canonical clinical tables because many point to patients without a true `patient_observations` parent in the current live dump.
4. Doctor linkage rollout
   Mirrored doctors, doctor-patient links, and legacy users are now in place. Remaining work is explicit profile-to-doctor linking for each active Django doctor account.
