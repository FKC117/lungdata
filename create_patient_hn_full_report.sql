-- Run only in lung_recent.
-- One row per (patient_id, normalized HN). Blank HNs are kept separate per patient.
-- This is a materialized reporting table: rebuild it after source-data changes.
-- No source table is changed.

SET SESSION group_concat_max_len = 1048576;

CREATE TABLE patient_hn_full_report AS
WITH
base AS (
  SELECT
    po.*,
    CASE
      WHEN NULLIF(TRIM(po.registration_no), '') IS NULL THEN CONCAT('NO_HN_PATIENT_', po.patient_id)
      ELSE UPPER(TRIM(po.registration_no))
    END AS normalized_hn
  FROM patient_observations po
  WHERE po.is_draft = 0
),
history_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ',
      CONCAT('Marital: ', marital_status), CONCAT('Diet: ', dietary_habit),
      CONCAT('Height: ', height), CONCAT('Weight: ', weight), CONCAT('BMI: ', bmi),
      CONCAT('Alcohol: ', h_o_alcoholism), CONCAT('RT chest: ', rt_to_chest),
      CONCAT('Cancer history: ', cancer_history), CONCAT('Mutation: ', known_mutation),
      CONCAT('First diagnosis: ', first_diagnosis_date)), '') ORDER BY id SEPARATOR '\n') AS patient_history
  FROM patient_histories GROUP BY patient_observation_id
),
comorbidity_agg AS (
  SELECT patient_observation_id, GROUP_CONCAT(DISTINCT detail ORDER BY id SEPARATOR '\n') AS comorbidities
  FROM comorbidities GROUP BY patient_observation_id
),
diagnosis_agg AS (
  SELECT patient_observation_id, GROUP_CONCAT(DISTINCT detail ORDER BY id SEPARATOR '\n') AS diagnoses
  FROM diagnoses GROUP BY patient_observation_id
),
metastatic_agg AS (
  SELECT patient_observation_id, GROUP_CONCAT(DISTINCT value ORDER BY id SEPARATOR '\n') AS metastatic_sites
  FROM diagnosis_metastatic_sites GROUP BY patient_observation_id
),
histopathology_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('Detail: ', detail),
      CONCAT('Site: ', site), CONCAT('Type: ', type)), '') ORDER BY id SEPARATOR '\n') AS histopathologies
  FROM histopathologies GROUP BY patient_observation_id
),
ihc_detail_agg AS (
  SELECT ihc_id, GROUP_CONCAT(NULLIF(CONCAT_WS(': ', type, value), '') ORDER BY id SEPARATOR ', ') AS details
  FROM ihc_details GROUP BY ihc_id
),
ihc_agg AS (
  SELECT i.patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', i.date), d.details), '') ORDER BY i.id SEPARATOR '\n') AS ihc
  FROM ihcs i LEFT JOIN ihc_detail_agg d ON d.ihc_id = i.id
  GROUP BY i.patient_observation_id
),
molecular_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('Specimen: ', specimen),
      CONCAT('Method: ', method), CONCAT('Gene: ', gene), CONCAT('Exon: ', exon), CONCAT('Status: ', status)), '')
      ORDER BY id SEPARATOR '\n') AS molecular_pathologies
  FROM molecular_pathologies GROUP BY patient_observation_id
),
marker_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('Name: ', name),
      CONCAT('Value: ', value), CONCAT('Unit: ', unit)), '') ORDER BY id SEPARATOR '\n') AS cancer_markers
  FROM cancer_markers GROUP BY patient_observation_id
),
past_treatment_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), detail), '') ORDER BY id SEPARATOR '\n') AS past_treatments
  FROM past_treatment_histories GROUP BY patient_observation_id
),
clinical_staging_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('T: ', t), CONCAT('N: ', n),
      CONCAT('M: ', m), CONCAT('Result: ', result)), '') ORDER BY id SEPARATOR '\n') AS clinical_staging
  FROM staging_clinicals GROUP BY patient_observation_id
),
pathological_staging_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('T: ', t), CONCAT('N: ', n),
      CONCAT('M: ', m), CONCAT('Result: ', result)), '') ORDER BY id SEPARATOR '\n') AS pathological_staging
  FROM staging_pathologicals GROUP BY patient_observation_id
),
pathological_detail_agg AS (
  SELECT patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', date), CONCAT('LVSI: ', lvsi),
      CONCAT('PNI: ', pni), CONCAT('Margin: ', margin), CONCAT('Ki67: ', ki67)), '') ORDER BY id SEPARATOR '\n') AS pathological_details
  FROM staging_pathological_details GROUP BY patient_observation_id
),
chemo_modality_agg AS (
  SELECT patient_observation_detail_id, GROUP_CONCAT(DISTINCT detail ORDER BY id SEPARATOR ', ') AS modalities
  FROM chemotherapy_modalities GROUP BY patient_observation_detail_id
),
protocol_detail_agg AS (
  SELECT chemotherapy_protocol_id, GROUP_CONCAT(value ORDER BY id SEPARATOR ' + ') AS protocol_values
  FROM chemotherapy_protocol_details GROUP BY chemotherapy_protocol_id
),
chemo_protocol_agg AS (
  SELECT cp.patient_observation_detail_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(' ', p.protocol_values, CONCAT('Cycle: ', cp.cycle_no), cp.type), '')
      ORDER BY cp.id SEPARATOR '\n') AS protocols
  FROM chemotherapy_protocols cp LEFT JOIN protocol_detail_agg p ON p.chemotherapy_protocol_id = cp.id
  GROUP BY cp.patient_observation_detail_id
),
observation_detail_agg AS (
  SELECT pod.patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(' | ',
      CONCAT('Chemo protocol: ', pod.current_chemo_protocol), CONCAT('Chemo start: ', pod.chemo_starting_date),
      CONCAT('Chemo end: ', pod.chemo_end_date), CONCAT('Chemo cycle: ', pod.chemo_cycle_no),
      CONCAT('Line: ', pod.line_of_treatment), CONCAT('Progression: ', pod.disease_progression_status),
      CONCAT('Survival: ', pod.survival_status), CONCAT('PFS: ', pod.pfs), CONCAT('Overall survival: ', pod.overall_survival),
      CONCAT('RECIST: ', pod.recist_1_result), CONCAT('iRECIST: ', pod.irecist_result),
      CONCAT('Pathological response: ', pod.pathological_response_rate_result),
      CONCAT('Modalities: ', cm.modalities), CONCAT('Protocols: ', cp.protocols)), '')
      ORDER BY pod.id SEPARATOR '\n') AS observation_details
  FROM patient_observation_details pod
  LEFT JOIN chemo_modality_agg cm ON cm.patient_observation_detail_id = pod.id
  LEFT JOIN chemo_protocol_agg cp ON cp.patient_observation_detail_id = pod.id
  GROUP BY pod.patient_observation_id
),
surgical_laterality_agg AS (
  SELECT surgery_id, GROUP_CONCAT(DISTINCT value ORDER BY id SEPARATOR ', ') AS lateralities
  FROM surgical_lateralities GROUP BY surgery_id
),
surgery_agg AS (
  SELECT s.patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Date: ', s.surgery_date), CONCAT('Modality: ', s.modality),
      CONCAT('Laterality: ', l.lateralities)), '') ORDER BY s.id SEPARATOR '\n') AS surgeries
  FROM surgeries s LEFT JOIN surgical_laterality_agg l ON l.surgery_id = s.id
  GROUP BY s.patient_observation_id
),
radiotherapy_modality_agg AS (
  SELECT radiotherapy_schedule_id, GROUP_CONCAT(DISTINCT value ORDER BY id SEPARATOR ', ') AS modalities
  FROM radiotherapy_schedule_modalities GROUP BY radiotherapy_schedule_id
),
radiotherapy_site_agg AS (
  SELECT radiotherapy_schedule_id, GROUP_CONCAT(DISTINCT value ORDER BY id SEPARATOR ', ') AS sites
  FROM radiotherapy_schedule_sites GROUP BY radiotherapy_schedule_id
),
radiotherapy_agg AS (
  SELECT r.patient_observation_id,
    GROUP_CONCAT(NULLIF(CONCAT_WS(', ', CONCAT('Start: ', r.start_date), CONCAT('End: ', r.end_date),
      CONCAT('Intent: ', r.intent), CONCAT('Fraction: ', r.fraction), CONCAT('Fraction no: ', r.fraction_number),
      CONCAT('Dose: ', r.total_dose), CONCAT('Modalities: ', m.modalities), CONCAT('Sites: ', s.sites)), '')
      ORDER BY r.id SEPARATOR '\n') AS radiotherapy
  FROM radiotherapy_schedules r
  LEFT JOIN radiotherapy_modality_agg m ON m.radiotherapy_schedule_id = r.id
  LEFT JOIN radiotherapy_site_agg s ON s.radiotherapy_schedule_id = r.id
  GROUP BY r.patient_observation_id
)
SELECT
  b.patient_id,
  b.normalized_hn,
  GROUP_CONCAT(DISTINCT NULLIF(TRIM(b.registration_no), '') ORDER BY b.registration_no SEPARATOR ' ; ') AS registration_numbers,
  p.unique_id AS patient_unique_id,
  p.name AS patient_name,
  p.phone,
  p.email,
  p.nid,
  p.date_of_birth,
  p.age,
  p.gender,
  p.blood_group,
  p.area,
  p.police_station,
  p.district,
  p.socio_economic_status,
  p.type AS patient_type,
  COUNT(DISTINCT b.id) AS observation_count,
  GROUP_CONCAT(DISTINCT b.id ORDER BY b.id SEPARATOR ',') AS source_observation_ids,
  MIN(b.time) AS first_observation_time,
  MAX(b.time) AS last_observation_time,
  GROUP_CONCAT(DISTINCT DATE_FORMAT(b.time, '%Y-%m-%d %H:%i:%s') ORDER BY b.time SEPARATOR '\n') AS observation_times,
  GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR ' ; ') AS doctors,
  GROUP_CONCAT(DISTINCT c.name ORDER BY c.name SEPARATOR ' ; ') AS centers,
  GROUP_CONCAT(DISTINCT NULLIF(b.cancer_type, '') ORDER BY b.cancer_type SEPARATOR ' ; ') AS cancer_types,
  GROUP_CONCAT(DISTINCT NULLIF(b.laterality, '') ORDER BY b.laterality SEPARATOR ' ; ') AS observation_lateralities,
  GROUP_CONCAT(DISTINCT NULLIF(b.grade, '') ORDER BY b.grade SEPARATOR ' ; ') AS grades,
  GROUP_CONCAT(DISTINCT NULLIF(b.diagnosis_disease_group, '') ORDER BY b.diagnosis_disease_group SEPARATOR ' ; ') AS diagnosis_disease_groups,
  GROUP_CONCAT(DISTINCT NULLIF(b.diagnosis_subgroup, '') ORDER BY b.diagnosis_subgroup SEPARATOR ' ; ') AS diagnosis_subgroups,
  GROUP_CONCAT(DISTINCT NULLIF(b.diagnosis_primary_site, '') ORDER BY b.diagnosis_primary_site SEPARATOR ' ; ') AS diagnosis_primary_sites,
  GROUP_CONCAT(DISTINCT NULLIF(b.diagnosis_laterility, '') ORDER BY b.diagnosis_laterility SEPARATOR ' ; ') AS diagnosis_lateralities,
  GROUP_CONCAT(DISTINCT h.patient_history ORDER BY b.time SEPARATOR '\n---\n') AS patient_history,
  GROUP_CONCAT(DISTINCT co.comorbidities ORDER BY b.time SEPARATOR '\n---\n') AS comorbidities,
  GROUP_CONCAT(DISTINCT dg.diagnoses ORDER BY b.time SEPARATOR '\n---\n') AS diagnoses,
  GROUP_CONCAT(DISTINCT ms.metastatic_sites ORDER BY b.time SEPARATOR '\n---\n') AS metastatic_sites,
  GROUP_CONCAT(DISTINCT hp.histopathologies ORDER BY b.time SEPARATOR '\n---\n') AS histopathologies,
  GROUP_CONCAT(DISTINCT ih.ihc ORDER BY b.time SEPARATOR '\n---\n') AS ihc,
  GROUP_CONCAT(DISTINCT mp.molecular_pathologies ORDER BY b.time SEPARATOR '\n---\n') AS molecular_pathologies,
  GROUP_CONCAT(DISTINCT cmk.cancer_markers ORDER BY b.time SEPARATOR '\n---\n') AS cancer_markers,
  GROUP_CONCAT(DISTINCT pt.past_treatments ORDER BY b.time SEPARATOR '\n---\n') AS past_treatments,
  GROUP_CONCAT(DISTINCT sc.clinical_staging ORDER BY b.time SEPARATOR '\n---\n') AS clinical_staging,
  GROUP_CONCAT(DISTINCT sp.pathological_staging ORDER BY b.time SEPARATOR '\n---\n') AS pathological_staging,
  GROUP_CONCAT(DISTINCT sd.pathological_details ORDER BY b.time SEPARATOR '\n---\n') AS pathological_details,
  GROUP_CONCAT(DISTINCT od.observation_details ORDER BY b.time SEPARATOR '\n---\n') AS chemotherapy_and_response_details,
  GROUP_CONCAT(DISTINCT su.surgeries ORDER BY b.time SEPARATOR '\n---\n') AS surgeries,
  GROUP_CONCAT(DISTINCT rt.radiotherapy ORDER BY b.time SEPARATOR '\n---\n') AS radiotherapy,
  MIN(b.created_at) AS first_source_created_at,
  MAX(b.updated_at) AS last_source_updated_at
FROM base b
JOIN patients p ON p.id = b.patient_id
LEFT JOIN doctors d ON d.id = b.doctor_id
LEFT JOIN centers c ON c.id = b.center_id
LEFT JOIN history_agg h ON h.patient_observation_id = b.id
LEFT JOIN comorbidity_agg co ON co.patient_observation_id = b.id
LEFT JOIN diagnosis_agg dg ON dg.patient_observation_id = b.id
LEFT JOIN metastatic_agg ms ON ms.patient_observation_id = b.id
LEFT JOIN histopathology_agg hp ON hp.patient_observation_id = b.id
LEFT JOIN ihc_agg ih ON ih.patient_observation_id = b.id
LEFT JOIN molecular_agg mp ON mp.patient_observation_id = b.id
LEFT JOIN marker_agg cmk ON cmk.patient_observation_id = b.id
LEFT JOIN past_treatment_agg pt ON pt.patient_observation_id = b.id
LEFT JOIN clinical_staging_agg sc ON sc.patient_observation_id = b.id
LEFT JOIN pathological_staging_agg sp ON sp.patient_observation_id = b.id
LEFT JOIN pathological_detail_agg sd ON sd.patient_observation_id = b.id
LEFT JOIN observation_detail_agg od ON od.patient_observation_id = b.id
LEFT JOIN surgery_agg su ON su.patient_observation_id = b.id
LEFT JOIN radiotherapy_agg rt ON rt.patient_observation_id = b.id
GROUP BY b.patient_id, b.normalized_hn,
  p.unique_id, p.name, p.phone, p.email, p.nid, p.date_of_birth, p.age, p.gender,
  p.blood_group, p.area, p.police_station, p.district, p.socio_economic_status, p.type;

ALTER TABLE patient_hn_full_report
  ADD PRIMARY KEY (patient_id, normalized_hn),
  ADD INDEX idx_patient_unique_id (patient_unique_id),
  ADD INDEX idx_registration_numbers (registration_numbers(100));
