<?php

declare(strict_types=1);

$db = new PDO(
    'mysql:host=127.0.0.1;port=3306;dbname=lung_recent',
    'root',
    getenv('DB_PASSWORD'),
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

$sql = <<<'SQL'
SELECT
  (SELECT COUNT(*) FROM patient_observations WHERE is_draft = 0) AS published_observations,
  (SELECT COUNT(DISTINCT patient_id) FROM patient_observations WHERE is_draft = 0) AS distinct_patients,
  (SELECT COUNT(*) FROM patient_observations WHERE is_draft = 0 AND NULLIF(TRIM(registration_no), '') IS NOT NULL) AS rows_with_hn,
  (SELECT COUNT(DISTINCT NULLIF(TRIM(registration_no), '')) FROM patient_observations WHERE is_draft = 0) AS distinct_hn,
  (SELECT COUNT(*) FROM (
    SELECT registration_no
    FROM patient_observations
    WHERE is_draft = 0 AND NULLIF(TRIM(registration_no), '') IS NOT NULL
    GROUP BY registration_no HAVING COUNT(*) > 1
  ) g) AS repeated_hn_groups,
  (SELECT COALESCE(SUM(n), 0) FROM (
    SELECT COUNT(*) AS n
    FROM patient_observations
    WHERE is_draft = 0 AND NULLIF(TRIM(registration_no), '') IS NOT NULL
    GROUP BY registration_no HAVING COUNT(*) > 1
  ) g) AS rows_in_repeated_hn_groups,
  (SELECT COUNT(*) FROM (
    SELECT registration_no
    FROM patient_observations
    WHERE is_draft = 0 AND NULLIF(TRIM(registration_no), '') IS NOT NULL
    GROUP BY registration_no HAVING COUNT(DISTINCT patient_id) > 1
  ) g) AS hns_used_by_multiple_patients,
  (SELECT COUNT(*) FROM (
    SELECT patient_id, registration_no
    FROM patient_observations
    WHERE is_draft = 0 AND NULLIF(TRIM(registration_no), '') IS NOT NULL
    GROUP BY patient_id, registration_no HAVING COUNT(*) > 1
  ) g) AS same_patient_same_hn_multiple_observations
SQL;

echo json_encode($db->query($sql)->fetch(PDO::FETCH_ASSOC), JSON_PRETTY_PRINT) . PHP_EOL;
