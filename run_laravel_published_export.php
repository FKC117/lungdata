<?php

declare(strict_types=1);

$project = 'C:\\Users\\Lenovo\\Desktop\\django error\\lung\\legacy_laravel_react_2026_08_13\\api';
$output = __DIR__ . DIRECTORY_SEPARATOR . 'lung_recent_published_observations.xlsx';

require $project . DIRECTORY_SEPARATOR . 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';

$app = require $project . DIRECTORY_SEPARATOR . 'bootstrap' . DIRECTORY_SEPARATOR . 'app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$request = Illuminate\Http\Request::create('/admin/download-patient-observations', 'POST');
$filter = $app->make(App\Filters\PatientObservationFilter::class);
$controller = $app->make(Modules\Admin\Http\Controllers\DownloadController::class);
$response = $controller->patientObservation($request, $filter);

if (!$response instanceof Symfony\Component\HttpFoundation\BinaryFileResponse) {
    throw new RuntimeException('The Laravel exporter did not return an Excel download response.');
}

$temporaryFile = $response->getFile()->getPathname();
if (!copy($temporaryFile, $output)) {
    throw new RuntimeException('Could not copy the generated Excel file to the workspace.');
}

echo $output . PHP_EOL;
