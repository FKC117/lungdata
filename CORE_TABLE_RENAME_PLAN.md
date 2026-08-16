# Core Table Rename Plan

Date: August 16, 2026

## Purpose

This plan documents the exact core clinical table renames needed to bring the canonical Django database closer to the legacy MySQL schema.

These are structural renames, not just field additions. They affect the live shape of the local canonical database and must be done carefully.

## Current Situation

The local canonical database currently contains the core clinical tables under Django default names such as:

- `clinical_registry_patient`
- `clinical_registry_clinicalobservation`
- `clinical_registry_patienthistory`
- `clinical_registry_treatmentcycle`

The legacy schema expects names such as:

- `patients`
- `patient_observations`
- `patient_histories`
- `patient_observation_details`

## Exact Rename Map

| Current canonical table | Target legacy-style table |
| --- | --- |
| `clinical_registry_patient` | `patients` |
| `clinical_registry_clinicalobservation` | `patient_observations` |
| `clinical_registry_patienthistory` | `patient_histories` |
| `clinical_registry_smokinghistory` | `smoking_histories` |
| `clinical_registry_tuberculosishistory` | `tb_histories` |
| `clinical_registry_covidhistory` | `covid_histories` |
| `clinical_registry_diagnosis` | `diagnoses` |
| `clinical_registry_diagnosismetastaticsite` | `diagnosis_metastatic_sites` |
| `clinical_registry_comorbidity` | `comorbidities` |
| `clinical_registry_histopathology` | `histopathologies` |
| `clinical_registry_molecularpathology` | `molecular_pathologies` |
| `clinical_registry_cancermarker` | `cancer_markers` |
| `clinical_registry_clinicalstaging` | `staging_clinicals` |
| `clinical_registry_pathologicalstaging` | `staging_pathologicals` |
| `clinical_registry_pathologicalstagingdetail` | `staging_pathological_details` |
| `clinical_registry_immunohistochemistry` | `ihcs` |
| `clinical_registry_ihcdetail` | `ihc_details` |
| `clinical_registry_treatmentcycle` | `patient_observation_details` |
| `clinical_registry_treatmentcycleprogressionsite` | `patient_observation_response_rate_progression_sites` |
| `clinical_registry_chemotherapyprotocol` | `chemotherapy_protocols` |
| `clinical_registry_chemotherapyprotocoldetail` | `chemotherapy_protocol_details` |
| `clinical_registry_chemotherapymodality` | `chemotherapy_modalities` |
| `clinical_registry_pasttreatmenthistory` | `past_treatment_histories` |
| `clinical_registry_radiotherapyschedule` | `radiotherapy_schedules` |
| `clinical_registry_radiotherapyschedulesite` | `radiotherapy_schedule_sites` |
| `clinical_registry_radiotherapyschedulemodality` | `radiotherapy_schedule_modalities` |
| `clinical_registry_surgery` | `surgeries` |
| `clinical_registry_surgicallaterality` | `surgical_lateralities` |

## Why This Needs Care

1. These renames touch the main canonical data tables, not only lookup tables.
2. Django migrations will need to rename tables without losing data.
3. Foreign key constraints and indexes must remain intact after rename.
4. Admin, serializers, import commands, and APIs should continue working after the rename because they use models, but the migration itself must be correct.

## Safe Execution Order

1. Confirm the rename map.
2. Add `db_table` to the core clinical models.
3. Generate Django migrations that perform `AlterModelTable`.
4. Inspect the generated migration file carefully before applying it.
5. Run `migrate`.
6. Run `manage.py check`.
7. Run safe import backfill again.
8. Spot-check row counts and a few key clinical records.

## Expected Outcome

After this pass, the canonical Django database will be much closer to the legacy schema in both:

- field naming
- table naming

That will reduce future deployment risk when validating against the live dataset.
