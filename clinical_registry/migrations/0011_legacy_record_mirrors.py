from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clinical_registry", "0010_legacy_doctor_center_mirrors"),
    ]

    operations = [
        migrations.CreateModel(
            name="CancerMarkerRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
                ("unit", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_cancer_marker_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ChemotherapyModalityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_chemotherapy_modality_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ChemotherapyProtocolRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_chemotherapy_protocol_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ComorbidityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_comorbidity_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="CovidVaccineCompanyRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_covid_vaccine_company_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiagnosisDiseaseGroupRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_diagnosis_disease_group_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiagnosisLaterilityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_diagnosis_laterility_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiagnosisMetastaticSiteRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_diagnosis_metastatic_site_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiagnosisPrimarySiteRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_diagnosis_primary_site_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiseaseProgressionStatusRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_disease_progression_status_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="HistopathologyRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
                ("type", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_histopathology_records", "ordering": ["type", "name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="IhcRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_ihc_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="LineOfTreatmentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_line_of_treatment_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="MolecularPathologyRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("group", models.CharField(max_length=191)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_molecular_pathology_records", "ordering": ["group", "name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="RadiotherapyScheduleIntentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("value", models.TextField()),
            ],
            options={"db_table": "clinical_radiotherapy_schedule_intent_records", "ordering": ["value", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="RadiotherapyScheduleRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("type", models.CharField(max_length=191)),
                ("value", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_radiotherapy_schedule_records", "ordering": ["type", "value", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ResponseRateCalculationRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("target_lasion", models.CharField(max_length=191)),
                ("non_target_lasion", models.CharField(max_length=191)),
                ("new_lasion", models.CharField(max_length=191)),
                ("result", models.CharField(max_length=191)),
                ("type", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_response_rate_calculation_records", "ordering": ["type", "result", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ResponseRateRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("type", models.CharField(max_length=191)),
                ("group", models.CharField(max_length=191)),
                ("value", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_response_rate_records", "ordering": ["type", "group", "value", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="SocioEconomicStatusRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_socio_economic_status_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="StagingCalculationRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("t", models.CharField(max_length=191)),
                ("n", models.CharField(max_length=191)),
                ("m", models.CharField(max_length=191)),
                ("result", models.CharField(max_length=191)),
                ("type", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_staging_calculation_records", "ordering": ["type", "result", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="SurgicalLateralityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("value", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_surgical_laterality_records", "ordering": ["value", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="SurgeryModalityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_surgery_modality_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="SurvivalStatusRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={"db_table": "clinical_survival_status_records", "ordering": ["name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="DiagnosisDiseaseSubgroupRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
                ("diagnosis_disease_group_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subgroups", to="clinical_registry.diagnosisdiseasegrouprecord")),
            ],
            options={"db_table": "clinical_diagnosis_disease_subgroup_records", "ordering": ["diagnosis_disease_group_record__name", "name", "legacy_id"]},
        ),
        migrations.CreateModel(
            name="ExonRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("value", models.CharField(max_length=191)),
                ("molecular_pathology_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="exons", to="clinical_registry.molecularpathologyrecord")),
            ],
            options={"db_table": "clinical_exon_records", "ordering": ["molecular_pathology_record__name", "value", "legacy_id"]},
        ),
    ]
