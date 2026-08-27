"""
Populates the database with realistic demo data across every module so
the Administrative Dashboard (and manual/demo walkthroughs) show real
numbers instead of zeros. Depends on `seed_demo_users` having been run
first — it looks up the demo accounts by username rather than creating
its own.

Run with:
    python manage.py seed_demo_users
    python manage.py seed_demo_clinical_data
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import User
from core.models import Department
from patients.models import Patient, Provider
from clinical.models import Encounter, Diagnosis, Observation, Allergy
from laboratory.models import LaboratoryOrder, LaboratoryResult
from pharmacy.models import Medication, Prescription, DispensingRecord
from billing.models import Invoice, Payment

FIRST_NAMES = ["Adaeze", "Chinedu", "Folake", "Emeka", "Ngozi", "Tunde",
               "Amara", "Kelechi", "Bisi", "Obinna", "Yewande", "Segun"]
LAST_NAMES = ["Okafor", "Adeyemi", "Balogun", "Nwosu", "Eze", "Afolabi",
              "Chukwu", "Okonkwo", "Adebayo", "Ibrahim", "Yusuf", "Danjuma"]

COMPLAINTS = [
    "Persistent headache and dizziness", "Fever and chills for 3 days",
    "Abdominal pain after meals", "Shortness of breath on exertion",
    "Lower back pain radiating to left leg", "Sore throat and cough",
    "Routine antenatal check-up", "Follow-up for hypertension management",
]

LAB_TESTS = [
    ("Full Blood Count", "6690-2"), ("Malaria Parasite Test", "32700-7"),
    ("Fasting Blood Sugar", "1558-6"), ("Widal Test", "5390-4"),
    ("Urinalysis", "24357-6"), ("Liver Function Test", "24325-3"),
]

MEDICATIONS = [
    ("Paracetamol", "500mg", "Tablet", "50.00"),
    ("Amoxicillin", "500mg", "Capsule", "120.00"),
    ("Artemether/Lumefantrine", "20/120mg", "Tablet", "800.00"),
    ("Metformin", "500mg", "Tablet", "90.00"),
    ("Amlodipine", "5mg", "Tablet", "150.00"),
    ("Ibuprofen", "400mg", "Tablet", "60.00"),
]


class Command(BaseCommand):
    help = "Seeds realistic demo clinical, laboratory, pharmacy, and billing data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--patients", type=int, default=25,
            help="Number of demo patients to create (default: 25)."
        )

    def handle(self, *args, **options):
        try:
            doctor = User.objects.get(username="doctor")
            nurse = User.objects.get(username="nurse")
            labtech = User.objects.get(username="labtech")
            pharmacist = User.objects.get(username="pharmacist")
            billing_officer = User.objects.get(username="billing")
        except User.DoesNotExist:
            raise CommandError(
                "Demo users not found. Run `python manage.py seed_demo_users` first."
            )

        department, _ = Department.objects.get_or_create(name="General Medicine")
        Department.objects.get_or_create(name="Paediatrics")
        Department.objects.get_or_create(name="Obstetrics & Gynaecology")

        Provider.objects.get_or_create(
            user=doctor, defaults={"license_number": "MDCN-10234", "specialty": "General Practice", "department": department}
        )

        medications = []
        for name, strength, form, price in MEDICATIONS:
            med, _ = Medication.objects.get_or_create(
                name=name, defaults={"strength": strength, "form": form, "unit_price": price, "stock_quantity": 200}
            )
            medications.append(med)

        n_patients = options["patients"]
        patients = []
        for i in range(n_patients):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            dob = date.today() - timedelta(days=random.randint(365 * 1, 365 * 80))
            patient = Patient.objects.create(
                first_name=first, last_name=last, date_of_birth=dob,
                gender=random.choice(["M", "F"]),
                phone_number=f"080{random.randint(10000000, 99999999)}",
                address="Lagos, Nigeria",
                registered_by=random.choice([nurse, billing_officer]),
            )
            # backdate created_at across the last 7 days so the dashboard's
            # 7-day trend chart has a realistic, non-flat shape
            days_ago = random.randint(0, 6)
            Patient.objects.filter(pk=patient.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            )
            patients.append(patient)
            if random.random() < 0.15:
                Allergy.objects.create(
                    patient=patient, substance=random.choice(["Penicillin", "Sulpha drugs", "Latex"]),
                    reaction="Skin rash", severity=random.choice(["MILD", "MODERATE", "SEVERE"]),
                )

        self.stdout.write(self.style.SUCCESS(f"Created {len(patients)} patients."))

        encounter_count = lab_order_count = lab_result_count = 0
        prescription_count = dispensed_count = invoice_count = payment_count = 0

        for patient in patients:
            n_encounters = random.randint(1, 2)
            for _ in range(n_encounters):
                encounter = Encounter.objects.create(
                    patient=patient, provider=Provider.objects.filter(user=doctor).first(),
                    department=department, status=Encounter.Status.COMPLETED,
                    chief_complaint=random.choice(COMPLAINTS),
                    examination_findings="Findings consistent with reported symptoms.",
                    treatment_plan="Symptomatic management and follow-up as needed.",
                )
                encounter_count += 1

                Observation.objects.create(
                    encounter=encounter, recorded_by=nurse,
                    temperature_c=round(random.uniform(36.1, 39.0), 1),
                    blood_pressure_systolic=random.randint(105, 150),
                    blood_pressure_diastolic=random.randint(65, 95),
                    pulse_rate=random.randint(60, 100),
                    respiratory_rate=random.randint(14, 22),
                    weight_kg=round(random.uniform(45, 95), 1),
                )
                Diagnosis.objects.create(
                    encounter=encounter, description=f"Clinical impression: {random.choice(COMPLAINTS).lower()}",
                    is_primary=True,
                )

                # Lab order + result, most of the time
                if random.random() < 0.7:
                    test_name, loinc = random.choice(LAB_TESTS)
                    order = LaboratoryOrder.objects.create(
                        encounter=encounter, ordered_by=doctor, test_name=test_name,
                        loinc_code=loinc, status=LaboratoryOrder.Status.COMPLETED,
                    )
                    lab_order_count += 1
                    if random.random() < 0.8:
                        LaboratoryResult.objects.create(
                            order=order, performed_by=labtech,
                            result_value=str(round(random.uniform(4.0, 12.0), 1)),
                            unit="x10^9/L", reference_range="4.0-11.0",
                            is_abnormal=random.random() < 0.2,
                        )
                        lab_result_count += 1

                # Prescription + dispensing, most of the time
                lab_charge = "3500.00" if random.random() < 0.7 else "0.00"
                pharmacy_charge = "0.00"
                if random.random() < 0.6:
                    med = random.choice(medications)
                    qty = random.randint(5, 20)
                    rx = Prescription.objects.create(
                        encounter=encounter, medication=med, prescribed_by=doctor,
                        dosage_instructions="Take as directed", quantity=qty,
                        status=Prescription.Status.DISPENSED,
                    )
                    prescription_count += 1
                    if random.random() < 0.75:
                        DispensingRecord.objects.create(
                            prescription=rx, dispensed_by=pharmacist, quantity_dispensed=qty,
                        )
                        dispensed_count += 1
                        pharmacy_charge = str(Decimal(str(med.unit_price)) * qty)

                # Invoice + payment
                invoice = Invoice.objects.create(
                    patient=patient, encounter=encounter,
                    consultation_fee=Decimal("2000.00"), laboratory_charges=Decimal(lab_charge),
                    pharmacy_charges=Decimal(pharmacy_charge), created_by=billing_officer,
                )
                invoice_count += 1
                if random.random() < 0.65:
                    Payment.objects.create(
                        invoice=invoice, amount=invoice.total_amount,
                        method=random.choice(["CASH", "CARD", "TRANSFER"]),
                        received_by=billing_officer,
                    )
                    invoice.status = Invoice.Status.PAID
                    invoice.save(update_fields=["status"])
                    payment_count += 1
                elif random.random() < 0.5:
                    partial = round(float(invoice.total_amount) * 0.4, 2)
                    Payment.objects.create(
                        invoice=invoice, amount=partial, method="CASH", received_by=billing_officer,
                    )
                    invoice.status = Invoice.Status.PARTIALLY_PAID
                    invoice.save(update_fields=["status"])
                    payment_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {encounter_count} encounters, {lab_order_count} lab orders "
            f"({lab_result_count} with results), {prescription_count} prescriptions "
            f"({dispensed_count} dispensed), {invoice_count} invoices "
            f"({payment_count} with a payment recorded)."
        ))
        self.stdout.write(self.style.SUCCESS("Demo clinical data seeding complete."))
