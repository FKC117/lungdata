from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clinical_registry", "0005_canonical_lookup_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlcoholHistoryOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_alcohol_history_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CovidStatusOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_covid_status_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CovidVaccinationDoseOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_covid_vaccination_dose_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CovidVaccineOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_covid_vaccine_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MaritalStatusOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_marital_status_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SmokingStatusOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_smoking_status_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TuberculosisStatusOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_tuberculosis_status_options",
                "ordering": ["name"],
            },
        ),
    ]
