<?php

declare(strict_types=1);

$db = new PDO(
    'mysql:host=127.0.0.1;port=3306;dbname=lung_recent',
    'root',
    getenv('DB_PASSWORD'),
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

$exists = (int) $db->query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'lung_recent' AND table_name = 'patient_hn_full_report'")->fetchColumn();
if ($exists !== 0) {
    throw new RuntimeException('patient_hn_full_report already exists; refusing to overwrite it.');
}

$sql = file_get_contents(__DIR__ . DIRECTORY_SEPARATOR . 'create_patient_hn_full_report.sql');
if ($sql === false) {
    throw new RuntimeException('Could not read the reporting-table SQL file.');
}
$db->exec($sql);

$summary = $db->query('SELECT COUNT(*) AS report_rows, SUM(observation_count) AS source_observations, COUNT(DISTINCT patient_id) AS patients FROM patient_hn_full_report')->fetch(PDO::FETCH_ASSOC);
echo json_encode($summary, JSON_PRETTY_PRINT) . PHP_EOL;
