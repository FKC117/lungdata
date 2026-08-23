# Table Mirror Drift

Date: August 16, 2026

## `patient_observations`

Legacy columns confirmed in snapshot:

- `patient_id`
- `doctor_id`
- `center_id`
- `time`
- `registration_no`
- `laterality`
- `grade`
- `diagnosis_disease_group`
- `diagnosis_subgroup`
- `diagnosis_primary_site`
- `diagnosis_laterility`
- `cancer_type`
- `is_draft`
- timestamps

Current canonical model status:

- mirrored table name is correct
- all core legacy columns above are represented

Current extra helper fields still present:

- `observed_at`
- `consulting_doctor_name`
- `center_name`
- `diagnosis_laterality`
- `laterality_notes`
- `created_by`
- `deleted_at`
- `legacy_id`

Safe interpretation:

- no core live-data blocker remains for this table
- remaining drift is helper-field drift, not missing legacy structure

## `patient_histories`

Legacy columns confirmed in snapshot:

- `patient_observation_id`
- `marital_status`
- `dietary_habit`
- `height`
- `weight`
- `bmi`
- `h_o_alcoholism`
- `rt_to_chest`
- `cancer_history`
- `known_mutation`
- `first_diagnosis_date`
- timestamps

Current canonical model status:

- mirrored table name is correct
- all core legacy columns above are represented

Current extra helper fields still present:

- `height_cm`
- `weight_kg`
- `alcohol_history`
- `radiotherapy_to_chest`
- `family_cancer_history`
- `legacy_id`

Safe interpretation:

- no core live-data blocker remains for this table
- remaining drift is helper-field drift, not missing legacy structure

## Recommended Order

1. Keep current schema for now.
2. Finish backend logic against legacy-style fields first.
3. Remove helper duplicates only after serializers, imports, and React entry forms stop depending on them.
