<?php

declare(strict_types=1);

$db = new PDO(
    'mysql:host=127.0.0.1;port=3306;dbname=information_schema',
    'root',
    getenv('DB_PASSWORD'),
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

$tables = [
    'patients', 'patient_observations', 'doctors', 'centers',
    'patient_histories', 'comorbidities', 'diagnoses', 'diagnosis_metastatic_sites',
    'histopathologies', 'ihcs', 'ihc_details', 'molecular_pathologies', 'cancer_markers',
    'staging_clinicals', 'staging_pathologicals', 'staging_pathological_details',
    'patient_observation_details', 'chemotherapy_modalities', 'chemotherapy_protocols',
    'chemotherapy_protocol_details', 'surgeries', 'surgical_lateralities',
    'radiotherapy_schedules', 'radiotherapy_schedule_modalities', 'radiotherapy_schedule_sites',
    'past_treatment_histories'
];
$marks = implode(',', array_fill(0, count($tables), '?'));
$sql = "SELECT table_name AS source_table, GROUP_CONCAT(column_name ORDER BY ordinal_position SEPARATOR ', ') AS columns_list\n"
    . "FROM columns WHERE table_schema = 'lung_recent' AND table_name IN ($marks)\n"
    . "GROUP BY table_name ORDER BY table_name";
$stmt = $db->prepare($sql);
$stmt->execute($tables);
foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row) {
    echo $row['source_table'] . ': ' . $row['columns_list'] . PHP_EOL;
}
