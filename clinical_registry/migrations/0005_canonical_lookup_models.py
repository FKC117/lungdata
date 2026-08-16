from django.db import migrations, models


def seed_lookup_tables(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    GenderOption = apps.get_model("clinical_registry", "GenderOption")
    BloodGroupOption = apps.get_model("clinical_registry", "BloodGroupOption")
    DistrictOption = apps.get_model("clinical_registry", "DistrictOption")
    PoliceStationOption = apps.get_model("clinical_registry", "PoliceStationOption")
    SocioEconomicStatusOption = apps.get_model("clinical_registry", "SocioEconomicStatusOption")
    PatientTypeOption = apps.get_model("clinical_registry", "PatientTypeOption")
    Patient = apps.get_model("clinical_registry", "Patient")

    for value in ["Male", "Female", "Other"]:
        GenderOption.objects.get_or_create(name=value, defaults={"is_active": True})

    for value in [
        "A positive",
        "A negative",
        "B positive",
        "B negative",
        "AB positive",
        "AB negative",
        "O positive",
        "O negative",
    ]:
        BloodGroupOption.objects.get_or_create(name=value, defaults={"is_active": True})

    districts = set()
    police_station_pairs = set()
    socio_values = set()
    patient_type_values = set()

    if "police_stations" in existing_tables:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT TRIM(district), TRIM(name)
                FROM police_stations
                WHERE COALESCE(TRIM(district), '') <> ''
                  AND COALESCE(TRIM(name), '') <> ''
                """
            )
            for district_name, station_name in cursor.fetchall():
                districts.add(district_name)
                police_station_pairs.add((district_name, station_name))

    if "socio_economic_status_records" in existing_tables:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT TRIM(name)
                FROM socio_economic_status_records
                WHERE COALESCE(TRIM(name), '') <> ''
                """
            )
            for (value,) in cursor.fetchall():
                socio_values.add(value)

    for patient in Patient.objects.all().only(
        "district",
        "police_station",
        "socio_economic_status",
        "patient_type",
    ):
        if patient.district:
            districts.add(patient.district.strip())
        if patient.district and patient.police_station:
            police_station_pairs.add((patient.district.strip(), patient.police_station.strip()))
        if patient.socio_economic_status:
            socio_values.add(patient.socio_economic_status.strip())
        if patient.patient_type:
            patient_type_values.add(patient.patient_type.strip())

    district_map = {}
    for district_name in sorted(value for value in districts if value):
        district, _created = DistrictOption.objects.get_or_create(
            name=district_name,
            defaults={"is_active": True},
        )
        district_map[district_name] = district

    for district_name, station_name in sorted(police_station_pairs):
        if not district_name or not station_name:
            continue
        district = district_map.get(district_name)
        if district is None:
            district, _created = DistrictOption.objects.get_or_create(
                name=district_name,
                defaults={"is_active": True},
            )
            district_map[district_name] = district
        PoliceStationOption.objects.get_or_create(
            district=district,
            name=station_name,
            defaults={"is_active": True},
        )

    for value in sorted(item for item in socio_values if item):
        SocioEconomicStatusOption.objects.get_or_create(name=value, defaults={"is_active": True})

    for value in sorted(item for item in patient_type_values if item):
        PatientTypeOption.objects.get_or_create(name=value, defaults={"is_active": True})


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("clinical_registry", "0004_alter_patient_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BloodGroupOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_blood_group_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DistrictOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_district_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="GenderOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_gender_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="PatientTypeOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_patient_type_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SocioEconomicStatusOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "clinical_socio_economic_status_options",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="PoliceStationOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=191)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="police_stations",
                        to="clinical_registry.districtoption",
                    ),
                ),
            ],
            options={
                "db_table": "clinical_police_station_options",
                "ordering": ["district__name", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="policestationoption",
            constraint=models.UniqueConstraint(
                fields=("district", "name"),
                name="unique_police_station_per_district",
            ),
        ),
        migrations.RunPython(seed_lookup_tables, noop_reverse),
    ]
