from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clinical_registry", "0006_history_lookup_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiagnosisDiseaseGroupOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_diagnosis_disease_group_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DiagnosisLateralityOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_diagnosis_laterality_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DiagnosisMetastaticSiteOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_diagnosis_metastatic_site_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DiagnosisPrimarySiteOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_diagnosis_primary_site_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="HistopathologyOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191)),
                ("category", models.CharField(max_length=191)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_histopathology_options",
                "ordering": ["category", "name"],
            },
        ),
        migrations.CreateModel(
            name="IhcMarkerOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_ihc_marker_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MolecularPathologyOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("group", models.CharField(max_length=191)),
                ("name", models.CharField(max_length=191)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_molecular_pathology_options",
                "ordering": ["group", "name"],
            },
        ),
        migrations.CreateModel(
            name="DiagnosisDiseaseSubgroupOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="subgroups",
                        to="clinical_registry.diagnosisdiseasegroupoption",
                    ),
                ),
            ],
            options={
                "db_table": "clinical_diagnosis_disease_subgroup_options",
                "ordering": ["group__name", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="diagnosisdiseasesubgroupoption",
            constraint=models.UniqueConstraint(
                fields=("group", "name"),
                name="unique_diagnosis_subgroup_per_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="histopathologyoption",
            constraint=models.UniqueConstraint(
                fields=("category", "name"),
                name="unique_histopathology_option",
            ),
        ),
        migrations.AddConstraint(
            model_name="molecularpathologyoption",
            constraint=models.UniqueConstraint(
                fields=("group", "name"),
                name="unique_molecular_pathology_option",
            ),
        ),
    ]
