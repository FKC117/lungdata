# Legacy Schema Mirror Plan

## Objective
Rebuild the Django data layer so it mirrors the live legacy MySQL schema as closely as possible before we continue expanding API, permissions, and React workflows.

The migration priority is:

1. Keep live-dataset compatibility.
2. Keep imports deterministic.
3. Reduce translation logic between legacy data and canonical Django models.
4. Add new application behavior on top of the mirrored schema instead of reshaping live data too early.

## Why We Are Changing Direction
The current `clinical_registry` app is only a partial mirror of the legacy system.

Some major clinical tables already map well enough to keep, but several critical areas are still normalized or invented:

- doctor ownership currently relies on new `created_by` fields instead of legacy `doctor_id`
- center linkage is flattened into text instead of mirrored as `center_id`
- lookup tables were rebuilt as new canonical option tables instead of mirroring legacy `*_records` tables
- some field names were normalized instead of kept 1:1 with legacy names

For a live system, this creates migration risk.

## Current Keep / Change Decision

### Keep As Base Clinical Mirror
These models are already close to legacy structure and should stay, with field-level adjustments where needed:

- `Patient`
- `ClinicalObservation`
- `PatientHistory`
- `SmokingHistory`
- `TuberculosisHistory`
- `CovidHistory`
- `Diagnosis`
- `DiagnosisMetastaticSite`
- `Comorbidity`
- `Histopathology`
- `MolecularPathology`
- `CancerMarker`
- `ClinicalStaging`
- `PathologicalStaging`
- `PathologicalStagingDetail`
- `Immunohistochemistry`
- `IHCDetail`
- `TreatmentCycle`
- `TreatmentCycleProgressionSite`
- `ChemotherapyProtocol`
- `ChemotherapyProtocolDetail`
- `ChemotherapyModality`
- `PastTreatmentHistory`
- `RadiotherapySchedule`
- `RadiotherapyScheduleSite`
- `RadiotherapyScheduleModality`
- `Surgery`
- `SurgicalLaterality`

### Rename / Remodel
These should be aligned more strictly to legacy naming and relations:

- `ClinicalObservation.consulting_doctor_name` -> mirror `doctor_id`
- `ClinicalObservation.center_name` -> mirror `center_id`
- `ClinicalObservation.observed_at` -> mirror legacy `time`
- `ClinicalObservation.diagnosis_laterality` -> mirror legacy `diagnosis_laterility`
- `PatientHistory.height_cm` -> mirror legacy `height`
- `PatientHistory.weight_kg` -> mirror legacy `weight`
- `PatientHistory.alcohol_history` -> mirror legacy `h_o_alcoholism`
- `PatientHistory.radiotherapy_to_chest` -> mirror legacy `rt_to_chest`
- `PatientHistory.family_cancer_history` -> mirror legacy `cancer_history`

### Add Mirror Models
These should be introduced as proper mirrored legacy tables:

- `Doctor`
- `DoctorPatient`
- `DoctorDegree`
- `DoctorRecognitionRecord`
- `Center`
- legacy lookup record tables such as:
  - `diagnosis_disease_group_records`
  - `diagnosis_disease_subgroup_records`
  - `diagnosis_primary_site_records`
  - `diagnosis_laterility_records`
  - `diagnosis_metastatic_site_records`
  - `histopathology_records`
  - `ihc_records`
  - `molecular_pathology_records`
  - `cancer_marker_records`
  - `chemotherapy_protocol_records`
  - `chemotherapy_modality_records`
  - `radiotherapy_schedule_records`
  - `radiotherapy_schedule_intent_records`
  - `surgery_modality_records`
  - `surgical_laterality_records`
  - `socio_economic_status_records`
  - `survival_status_records`
  - `disease_progression_status_records`
  - `line_of_treatment_records`
  - `response_rate_records`
  - `response_rate_calculation_records`
  - `staging_calculation_records`
  - `covid_vaccine_company_records`
  - `comorbidity_records`
  - `exon_records`

### Keep As App-Layer Helpers Only
These are still useful, but they should not define the core live-data truth:

- `DoctorProfile`
- `created_by` ownership fields
- normalized option models if they remain for UI convenience

## Implementation Strategy

### Phase 1: Freeze And Audit
1. Snapshot the full legacy schema from `lung_local`.
2. Snapshot the current Django schema and current model inventory.
3. Produce a table-by-table comparison:
   - mirrored already
   - partially mirrored
   - missing
4. Do not delete current working code yet.

### Phase 2: Introduce Mirror Models
1. Add legacy mirror models for doctors, centers, and record tables.
2. Add missing foreign keys using legacy names where safe.
3. Prefer `db_table` exact matches to live legacy table names.
4. Keep the current app running while the mirror layer is introduced.

### Phase 3: Align Current Clinical Models
1. Replace flattened text fields with mirrored FK relations where legacy already provides FK columns.
2. Restore legacy field names where practical.
3. Keep compatibility helpers in serializers instead of changing import meaning.

### Phase 4: Rewrite Import Around Mirror Truth
1. Import live data into mirrored structures first.
2. Derive React/API payloads from the mirrored schema.
3. Remove guesswork such as manual ownership assignment where legacy doctor relations exist.

### Phase 5: Rebuild Permission Logic Safely
1. Admin sees everything.
2. Doctor visibility is derived from mirrored legacy doctor relations.
3. New React-created data should attach to mirrored doctor/user linkage, not only `created_by`.

### Phase 6: Regression Validation
1. Row-count verification per table.
2. Null-pattern verification for critical columns.
3. FK integrity verification.
4. Published vs draft verification.
5. Spot-check against the legacy UI for several known patients.

## Step-By-Step Task List

### Task 1
Create a reusable schema snapshot command for the legacy DB.

Status: `in progress`

### Task 2
Create a mirror inventory document listing:

- legacy table
- current Django model
- match quality
- action required

Status: `pending`

### Task 3
Add mirrored `Doctor` and `Center` models.

Status: `pending`

### Task 4
Refactor `ClinicalObservation` toward mirrored `doctor_id` and `center_id`.

Status: `pending`

### Task 5
Introduce legacy `*_records` mirror models for lookup/reference tables.

Status: `pending`

### Task 6
Refactor import commands to use the mirror layer as primary truth.

Status: `pending`

### Task 7
Rework doctor visibility rules to use mirrored doctor relations from imported live data.

Status: `pending`

### Task 8
Re-verify patient detail screens and entry/edit workflows against the mirrored schema.

Status: `pending`

## Acceptance Criteria

- live dump can be imported without manual schema translation hacks
- doctors/centers/records follow real legacy foreign keys
- legacy row counts are reproducible
- admin and doctor access rules come from mirrored data truth
- React UI continues to work through the Django API without depending on guessed ownership
