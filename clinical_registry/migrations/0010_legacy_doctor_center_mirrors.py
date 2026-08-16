from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clinical_registry", "0009_record_ownership"),
    ]

    operations = [
        migrations.CreateModel(
            name="Center",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
            ],
            options={
                "db_table": "clinical_centers",
                "ordering": ["name", "legacy_id"],
            },
        ),
        migrations.CreateModel(
            name="DoctorRecognitionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("group", models.CharField(max_length=191)),
                ("value", models.CharField(max_length=191)),
            ],
            options={
                "db_table": "clinical_doctor_recognition_records",
                "ordering": ["group", "value", "legacy_id"],
            },
        ),
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("name", models.CharField(max_length=191)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("designation", models.CharField(blank=True, max_length=50)),
                ("department", models.CharField(blank=True, max_length=50)),
                ("institution", models.CharField(blank=True, max_length=255)),
                ("bmdc_number", models.CharField(blank=True, max_length=10)),
                ("photo", models.CharField(blank=True, max_length=55)),
                ("password", models.TextField(blank=True)),
                ("status", models.CharField(blank=True, max_length=10)),
                (
                    "center",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="doctors",
                        to="clinical_registry.center",
                    ),
                ),
            ],
            options={
                "db_table": "clinical_doctors",
                "ordering": ["name", "legacy_id"],
            },
        ),
        migrations.CreateModel(
            name="DoctorDegree",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                ("degree", models.CharField(max_length=50)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="degrees",
                        to="clinical_registry.doctor",
                    ),
                ),
            ],
            options={
                "db_table": "clinical_doctor_degrees",
                "ordering": ["doctor__name", "degree", "legacy_id"],
            },
        ),
        migrations.CreateModel(
            name="DoctorPatient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("legacy_id", models.PositiveBigIntegerField(unique=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="doctor_patients",
                        to="clinical_registry.doctor",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="doctor_links",
                        to="clinical_registry.patient",
                    ),
                ),
            ],
            options={
                "db_table": "clinical_doctor_patients",
                "ordering": ["doctor__name", "patient__name", "legacy_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="doctorpatient",
            constraint=models.UniqueConstraint(fields=("doctor", "patient"), name="unique_doctor_patient_link"),
        ),
        migrations.AddField(
            model_name="clinicalobservation",
            name="center",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="observations", to="clinical_registry.center"),
        ),
        migrations.AddField(
            model_name="clinicalobservation",
            name="doctor",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="observations", to="clinical_registry.doctor"),
        ),
    ]
