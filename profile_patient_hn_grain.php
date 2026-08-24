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
  COUNT(*) AS published_observations,
  COUNT(DISTINCT patient_id) AS distinct_patients,
  COUNT(DISTINCT CONCAT(patient_id, '|', CASE
    WHEN NULLIF(TRIM(registration_no), '') IS NULL THEN CONCAT('NO_HN_PATIENT_', patient_id)
    ELSE UPPER(TRIM(registration_no))
  END)) AS patient_hn_rows
FROM patient_observations
WHERE is_draft = 0
SQL;

echo json_encode($db->query($sql)->fetch(PDO::FETCH_ASSOC), JSON_PRETTY_PRINT) . PHP_EOL;
