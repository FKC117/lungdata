from difflib import SequenceMatcher

from django.core.management.base import BaseCommand

from clinical_registry.models import Doctor, DoctorProfile


def normalize_name(value):
    if not value:
        return ""
    normalized = value.lower()
    for token in ("prof.", "prof", "dr.", "dr", "md", ","):
        normalized = normalized.replace(token, " ")
    return " ".join(normalized.split())


def similarity_score(left, right):
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


class Command(BaseCommand):
    help = "Suggest likely DoctorProfile to mirrored Doctor links without changing any data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Include already linked doctor profiles as well.",
        )
        parser.add_argument(
            "--min-score",
            type=float,
            default=0.55,
            help="Minimum normalized-name similarity score to show as a suggestion.",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=3,
            help="Maximum number of suggestions to show per profile.",
        )

    def handle(self, *args, **options):
        include_all = options["all"]
        min_score = options["min_score"]
        top_n = options["top"]

        profiles = DoctorProfile.objects.select_related("user", "doctor").order_by("display_name", "user__username")
        if not include_all:
            profiles = profiles.filter(is_active=True, doctor__isnull=True)

        doctors = list(Doctor.objects.order_by("name", "legacy_id"))
        if not doctors:
            self.stdout.write(self.style.WARNING("No mirrored Doctor records exist yet."))
            return

        total_profiles = profiles.count()
        self.stdout.write(self.style.NOTICE(f"Profiles to review: {total_profiles}"))

        for profile in profiles:
            heading = (
                f"Profile #{profile.pk} | user={profile.user.username} | "
                f"display={profile.display_name or '-'} | linked_doctor={profile.doctor_id or '-'}"
            )
            self.stdout.write("")
            self.stdout.write(self.style.HTTP_INFO(heading))

            if profile.doctor_id and include_all:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Already linked to Doctor #{profile.doctor_id}: {profile.doctor.name}"
                    )
                )

            profile_name = normalize_name(profile.display_name or profile.user.get_full_name() or profile.user.username)
            profile_email = (profile.user.email or "").strip().lower()
            profile_phone = (profile.phone or "").strip()

            suggestions = []
            for doctor in doctors:
                doctor_name = normalize_name(doctor.name)
                name_score = similarity_score(profile_name, doctor_name)
                email_match = bool(profile_email and doctor.email and profile_email == doctor.email.strip().lower())
                phone_match = bool(profile_phone and doctor.phone and profile_phone == doctor.phone.strip())

                total_score = name_score
                if email_match:
                    total_score += 0.35
                if phone_match:
                    total_score += 0.20

                if total_score < min_score and not email_match and not phone_match:
                    continue

                signals = []
                if name_score:
                    signals.append(f"name={name_score:.2f}")
                if email_match:
                    signals.append("email-match")
                if phone_match:
                    signals.append("phone-match")

                suggestions.append(
                    {
                        "doctor": doctor,
                        "score": total_score,
                        "signals": ", ".join(signals) or "weak-match",
                    }
                )

            suggestions.sort(key=lambda item: (-item["score"], item["doctor"].legacy_id))
            if not suggestions:
                self.stdout.write("  No confident suggestions.")
                continue

            for index, suggestion in enumerate(suggestions[:top_n], start=1):
                doctor = suggestion["doctor"]
                self.stdout.write(
                    f"  {index}. Doctor #{doctor.pk} legacy={doctor.legacy_id} | "
                    f"{doctor.name} | email={doctor.email or '-'} | phone={doctor.phone or '-'} | "
                    f"score={suggestion['score']:.2f} | {suggestion['signals']}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "Suggestion run only. No DoctorProfile links were changed."
            )
        )
