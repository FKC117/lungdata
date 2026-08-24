-- LOCAL lung_recent DATABASE ONLY. Do not run on live production.
-- Observation 8: patient 6 is uniquely supported by the orphan-child timestamp.
-- Doctor 1 / center 1 is inferred from patient 6's existing published observation.
-- Original parent-row fields were not retained in the binlogs.

INSERT INTO patient_observations (
  id,
  patient_id,
  doctor_id,
  center_id,
  time,
  registration_no,
  laterality,
  grade,
  diagnosis_disease_group,
  diagnosis_subgroup,
  diagnosis_primary_site,
  diagnosis_laterility,
  cancer_type,
  is_draft,
  created_at,
  updated_at
) VALUES (
  8,
  6,
  1,
  1,
  '2025-01-04 10:32:52',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  'Lung',
  0,
  '2025-01-04 10:32:52',
  '2025-01-04 10:32:52'
)
ON DUPLICATE KEY UPDATE
  patient_id = VALUES(patient_id),
  doctor_id = VALUES(doctor_id),
  center_id = VALUES(center_id),
  time = VALUES(time),
  cancer_type = VALUES(cancer_type),
  is_draft = VALUES(is_draft),
  updated_at = VALUES(updated_at);

-- Verify:
-- SELECT id, patient_id, doctor_id, center_id, is_draft
-- FROM patient_observations WHERE id = 8;
