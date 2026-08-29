from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clinical_registry.models import (
    CancerMarker,
    ChemotherapyModality,
    ChemotherapyProtocol,
    ChemotherapyProtocolDetail,
    ClinicalObservation,
    ClinicalStaging,
    Comorbidity,
    CovidHistory,
    Diagnosis,
    DiagnosisMetastaticSite,
    Histopathology,
    IHCDetail,
    Immunohistochemistry,
    MolecularPathology,
    PastTreatmentHistory,
    PathologicalStaging,
    PathologicalStagingDetail,
    Patient,
    PatientHistory,
    RadiotherapySchedule,
    RadiotherapyScheduleModality,
    RadiotherapyScheduleSite,
    SmokingHistory,
    Surgery,
    SurgicalLaterality,
    TreatmentCycle,
    TreatmentCycleProgressionSite,
    TuberculosisHistory,
)


REGISTRY_ID = "DUMMY-1"


def observed_at(year: int, month: int, day: int) -> datetime:
    return timezone.make_aware(datetime(year, month, day, 9, 30))


class Command(BaseCommand):
    help = "Create or delete a complete, clearly labelled DUMMY 1 patient for UI testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete DUMMY 1 and every related dummy observation/record.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        existing = Patient.objects.filter(registry_id=REGISTRY_ID)
        if options["delete"]:
            deleted, _ = existing.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted DUMMY 1 ({deleted} related rows removed)."))
            return

        # Re-running the command replaces only this synthetic record chain.
        existing.delete()
        owner = get_user_model().objects.filter(is_superuser=True).first()
        patient = Patient.objects.create(
            registry_id=REGISTRY_ID,
            legacy_unique_id="DUMMY-UNIQUE-1",
            registration_no="DUMMY-REG-0001",
            name="DUMMY 1",
            phone="01700000001",
            email="dummy1@example.invalid",
            nid="DUMMY-NID-0001",
            date_of_birth=date(1972, 5, 24),
            age=54,
            gender=Patient.Gender.FEMALE,
            blood_group="O+",
            area="Demo Area",
            police_station="Demo Police Station",
            district="Dhaka",
            socio_economic_status="Middle income",
            passport="DUMMY-PASSPORT-1",
            patient_type="Demonstration",
            created_by=owner,
        )

        diagnosis_observation = ClinicalObservation.objects.create(
            patient=patient,
            observed_at=observed_at(2024, 5, 24),
            time=observed_at(2024, 5, 24),
            registration_no=patient.registration_no,
            consulting_doctor_name="Dr Demo Oncologist",
            center_name="Demo Cancer Center",
            cancer_type="Lung",
            diagnosis_disease_group="C34-Malignant neoplasm of bronchus and lung",
            diagnosis_subgroup="C34.1-Malignant neoplasm of upper lobe, right bronchus or lung",
            diagnosis_primary_site="Right lung",
            diagnosis_laterality="Right",
            diagnosis_laterility="Right",
            grade="3",
            laterality="Right lung",
            laterality_notes="Synthetic record for UI demonstration only.",
            created_by=owner,
        )
        history = PatientHistory.objects.create(
            observation=diagnosis_observation,
            marital_status="Married",
            dietary_habit="Mixed diet",
            height=162.0,
            height_cm=162.0,
            weight=68.0,
            weight_kg=68.0,
            bmi=25.91,
            h_o_alcoholism="No",
            alcohol_history="No",
            rt_to_chest="No",
            radiotherapy_to_chest="No",
            cancer_history="Family history present",
            family_cancer_history="Mother: breast cancer",
            known_mutation="EGFR exon 19 deletion",
            first_diagnosis_date=date(2024, 5, 24),
        )
        SmokingHistory.objects.create(
            patient_history=history,
            status="Former smoker",
            per_day=12,
            cigarettes_per_day=12,
            duration_in_year=20,
            duration_years=20,
            packs_per_year=12,
            pack_years=12,
            quit_period=5,
            quit_period_years=5,
        )
        TuberculosisHistory.objects.create(
            patient_history=history,
            status="Past TB",
            date=date(2010, 2, 1),
            treatment="Completed six-month anti-tuberculosis treatment.",
        )
        CovidHistory.objects.create(
            patient_history=history,
            status="Recovered",
            date=date(2022, 7, 15),
            vaccine_name="Pfizer-BioNTech",
            vaccination_dose="Booster dose",
        )
        Diagnosis.objects.create(
            observation=diagnosis_observation,
            detail="Stage IVA adenocarcinoma of the right lung with pleural metastasis.",
        )
        DiagnosisMetastaticSite.objects.create(observation=diagnosis_observation, value="Pleura")
        DiagnosisMetastaticSite.objects.create(observation=diagnosis_observation, value="Bone")
        Comorbidity.objects.create(observation=diagnosis_observation, detail="Type 2 diabetes mellitus")
        Comorbidity.objects.create(observation=diagnosis_observation, detail="Hypertension")
        Comorbidity.objects.create(observation=diagnosis_observation, detail="Hypothyroidism")
        Histopathology.objects.create(
            observation=diagnosis_observation,
            detail="Adenocarcinoma, lung primary",
            site="Right upper lobe",
            histology_type="Non-small cell lung carcinoma",
            observed_on=date(2024, 5, 30),
        )
        MolecularPathology.objects.create(
            observation=diagnosis_observation,
            specimen="Core biopsy",
            method="RT-PCR",
            gene="EGFR",
            exon="Exon 19 deletion",
            status="Positive/Detected/Mutated",
            observed_on=date(2024, 6, 4),
        )
        MolecularPathology.objects.create(
            observation=diagnosis_observation,
            specimen="Core biopsy",
            method="IHC",
            gene="ALK",
            exon="",
            status="Negative/Not detected/Wild type",
            observed_on=date(2024, 6, 4),
        )
        MolecularPathology.objects.create(
            observation=diagnosis_observation,
            specimen="Core biopsy",
            method="IHC",
            gene="ROS1",
            exon="",
            status="Negative/Not detected/Wild type",
            observed_on=date(2024, 6, 4),
        )
        for name, value, unit in (("CEA", "21.8", "ng/mL"), ("CA19.9", "39.5", "U/mL"), ("CYFRA 21-1", "7.3", "ng/mL")):
            CancerMarker.objects.create(
                observation=diagnosis_observation,
                name=name,
                value=value,
                unit=unit,
                observed_on=date(2024, 5, 24),
            )
        ClinicalStaging.objects.create(
            observation=diagnosis_observation,
            t="T3",
            n="N2",
            m="M1a",
            result="Stage IVA",
            date=date(2024, 5, 24),
            staged_on=date(2024, 5, 24),
        )
        PathologicalStaging.objects.create(
            observation=diagnosis_observation,
            t="pT3",
            n="pN2",
            m="pM1a",
            result="Stage IVA",
            date=date(2024, 5, 30),
            staged_on=date(2024, 5, 30),
        )
        PathologicalStagingDetail.objects.create(
            observation=diagnosis_observation,
            lvsi="Present",
            pni="Absent",
            margin="Not applicable",
            ki67="45%",
            date=date(2024, 5, 30),
            staged_on=date(2024, 5, 30),
        )
        ihc = Immunohistochemistry.objects.create(
            observation=diagnosis_observation,
            date=date(2024, 5, 30),
            observed_on=date(2024, 5, 30),
        )
        for marker, value in (("TTF-1", "Positive"), ("Napsin A", "Positive"), ("p40", "Negative"), ("PD-L1", "TPS 35%")):
            IHCDetail.objects.create(ihc=ihc, marker_type=marker, value=value)

        treatment_observation = ClinicalObservation.objects.create(
            patient=patient,
            observed_at=observed_at(2024, 6, 15),
            time=observed_at(2024, 6, 15),
            registration_no=patient.registration_no,
            consulting_doctor_name="Dr Demo Oncologist",
            center_name="Demo Cancer Center",
            cancer_type="Lung",
            diagnosis_disease_group=diagnosis_observation.diagnosis_disease_group,
            diagnosis_subgroup=diagnosis_observation.diagnosis_subgroup,
            diagnosis_primary_site="Right lung",
            diagnosis_laterality="Right",
            diagnosis_laterility="Right",
            grade="3",
            created_by=owner,
        )
        cycle = TreatmentCycle.objects.create(
            observation=treatment_observation,
            current_chemo_protocol="Carboplatin + Pemetrexed + Pembrolizumab",
            chemo_cycle_no="4",
            chemo_detail="Four induction cycles completed, followed by maintenance pemetrexed and pembrolizumab.",
            chemo_starting_date=date(2024, 6, 15),
            chemo_end_date=date(2024, 8, 17),
            line_of_treatment="First line",
            disease_progression_status="Partial response",
            disease_progression_status_date=date(2024, 8, 20),
            survival_status="Alive",
            survival_status_date=date(2025, 5, 24),
            recist_1_target_lesion="Partial response",
            recist_1_non_target_lesion="Stable disease",
            recist_1_new_lesion="No",
            recist_1_result="PR",
            recist_1_date=date(2024, 8, 20),
            recist_1_method_of_estimation="CT chest and abdomen",
            irecist_target_lesion="Partial response",
            irecist_non_target_lesion="Non-iUPD",
            irecist_new_lesion="No",
            irecist_result="iPR",
            irecist_date=date(2024, 8, 20),
            irecist_method_of_estimation="CT chest and abdomen",
            pathological_response_rate_target_lesion="Marked treatment effect",
            pathological_response_rate_non_target_lesion="Not applicable",
            pathological_response_rate_new_lesion="No",
            pathological_response_rate_result="Major pathological response",
            pathological_response_rate_date=date(2024, 8, 20),
            pathological_method_of_estimation="Histopathology review",
            pfs="12 months",
            progression_free_survival="12 months",
            overall_survival="18 months",
        )
        TreatmentCycleProgressionSite.objects.create(treatment_cycle=cycle, site_type="Pleura", value="Decreased pleural nodularity")
        protocol = ChemotherapyProtocol.objects.create(treatment_cycle=cycle, cycle_no=4, protocol_type="Carboplatin + Pemetrexed")
        ChemotherapyProtocolDetail.objects.create(chemotherapy_protocol=protocol, value="Carboplatin AUC 5")
        ChemotherapyProtocolDetail.objects.create(chemotherapy_protocol=protocol, value="Pemetrexed 500 mg/m2")
        ChemotherapyModality.objects.create(treatment_cycle=cycle, detail="Chemo-immunotherapy")
        PastTreatmentHistory.objects.create(observation=treatment_observation, detail="No prior systemic therapy", date=date(2024, 6, 15))
        radiotherapy = RadiotherapySchedule.objects.create(
            observation=treatment_observation,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 21),
            intent="Palliative",
            fraction="3 Gy",
            fraction_number="10",
            total_dose="30",
        )
        RadiotherapyScheduleSite.objects.create(radiotherapy_schedule=radiotherapy, value="Right lung")
        RadiotherapyScheduleModality.objects.create(radiotherapy_schedule=radiotherapy, value="IMRT")
        surgery = Surgery.objects.create(
            observation=treatment_observation,
            surgery_date=date(2024, 10, 5),
            modality="Video-assisted thoracoscopic wedge resection",
        )
        SurgicalLaterality.objects.create(surgery=surgery, value="Right")

        follow_up_observation = ClinicalObservation.objects.create(
            patient=patient,
            observed_at=observed_at(2025, 5, 24),
            time=observed_at(2025, 5, 24),
            registration_no=patient.registration_no,
            consulting_doctor_name="Dr Demo Oncologist",
            center_name="Demo Cancer Center",
            cancer_type="Lung",
            diagnosis_disease_group=diagnosis_observation.diagnosis_disease_group,
            diagnosis_subgroup=diagnosis_observation.diagnosis_subgroup,
            diagnosis_primary_site="Right lung",
            diagnosis_laterality="Right",
            diagnosis_laterility="Right",
            grade="3",
            created_by=owner,
        )
        for name, value, unit in (("CEA", "5.9", "ng/mL"), ("CA19.9", "18.1", "U/mL"), ("CYFRA 21-1", "2.2", "ng/mL")):
            CancerMarker.objects.create(
                observation=follow_up_observation,
                name=name,
                value=value,
                unit=unit,
                observed_on=date(2025, 5, 24),
            )

        self.stdout.write(self.style.SUCCESS(
            f"Created DUMMY 1 ({patient.registry_id}) with 3 observations and complete related test data."
        ))
