from django.db.models import Q

from clinical_registry.models import ClinicalObservation, DoctorProfile, Patient


def get_active_doctor_profile(user):
    if not user or not user.is_authenticated:
        return None
    try:
        profile = user.doctor_profile
    except DoctorProfile.DoesNotExist:
        return None
    return profile if profile.is_active else None


def get_linked_legacy_doctor(user):
    profile = get_active_doctor_profile(user)
    return profile.doctor if profile and profile.doctor_id else None


def user_is_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff))


def scope_patients_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()
    if user_is_admin(user):
        return queryset
    legacy_doctor = get_linked_legacy_doctor(user)
    if legacy_doctor:
        return queryset.filter(
            Q(doctor_links__doctor=legacy_doctor) | Q(observations__doctor=legacy_doctor)
        ).distinct()
    return queryset.filter(created_by=user)


def scope_observations_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()
    if user_is_admin(user):
        return queryset
    legacy_doctor = get_linked_legacy_doctor(user)
    if legacy_doctor:
        return queryset.filter(
            Q(doctor=legacy_doctor) | Q(patient__doctor_links__doctor=legacy_doctor)
        ).distinct()
    return queryset.filter(created_by=user)


def user_can_access_patient(user, patient):
    return scope_patients_for_user(Patient.objects.filter(pk=patient.pk), user).exists()


def user_can_access_observation(user, observation):
    return scope_observations_for_user(
        ClinicalObservation.objects.filter(pk=observation.pk),
        user,
    ).exists()


def user_can_edit_patient(user, patient):
    return user_can_access_patient(user, patient)


def user_can_edit_observation(user, observation):
    return user_can_access_observation(user, observation)
