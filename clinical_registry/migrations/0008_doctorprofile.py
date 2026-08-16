from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clinical_registry", "0007_diagnosis_lookup_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DoctorProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("display_name", models.CharField(blank=True, max_length=191)),
                ("designation", models.CharField(blank=True, max_length=191)),
                ("department", models.CharField(blank=True, max_length=191)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("registration_number", models.CharField(blank=True, max_length=64)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="doctor_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "clinical_doctor_profiles",
                "ordering": ["display_name", "user__username"],
            },
        ),
    ]
