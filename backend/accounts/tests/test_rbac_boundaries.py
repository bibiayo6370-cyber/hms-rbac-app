"""
Security evaluation suite for Chapter 4 (System Testing).

This suite is the empirical evidence behind the RBAC claims in Section`
3.3.2. It does not merely check that endpoints require login — it
specifically asserts the NON-INHERITING PEER BOUNDARIES: that a Doctor,
despite being clinical staff, is just as forbidden from writing a Lab
Result or dispensing a Medication as a member of the public would be.
Each professional role is a peer, not a hierarchy, except for the
Super Admin / Admin tier which is explicitly hierarchical and expected
to pass everywhere.

Run with:
    python manage.py test accounts.tests.test_rbac_boundaries
"""
from datetime import date

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User, Role
from core.models import Department
from patients.models import Patient
from clinical.models import Encounter
from laboratory.models import LaboratoryOrder
from pharmacy.models import Medication, Prescription
from billing.models import Invoice


class RBACBoundaryTestCase(APITestCase):
    """
    Base class: creates one user per role and a minimal set of fixture
    records (department, patient, encounter, medication, prescription,
    lab order, invoice) that each boundary test writes against.
    """

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="General Medicine")

        cls.users = {}
        for role in Role.values:
            user = User.objects.create_user(
                username=f"test_{role.lower()}",
                password="TestPass123!",
                role=role,
                first_name=role.title(),
                last_name="Tester",
            )
            cls.users[role] = user

        cls.patient = Patient.objects.create(
            first_name="Jane", last_name="Doe",
            date_of_birth=date(1990, 1, 1), gender="F",
            registered_by=cls.users[Role.NURSE],
        )
        cls.encounter = Encounter.objects.create(
            patient=cls.patient, department=cls.department,
            chief_complaint="Fever and headache",
        )
        cls.medication = Medication.objects.create(
            name="Paracetamol", strength="500mg", form="Tablet",
            unit_price="50.00", stock_quantity=100,
        )
        cls.prescription = Prescription.objects.create(
            encounter=cls.encounter, medication=cls.medication,
            prescribed_by=cls.users[Role.DOCTOR],
            dosage_instructions="1 tablet twice daily", quantity=10,
        )
        cls.lab_order = LaboratoryOrder.objects.create(
            encounter=cls.encounter, ordered_by=cls.users[Role.DOCTOR],
            test_name="Full Blood Count",
        )
        cls.invoice = Invoice.objects.create(
            patient=cls.patient, encounter=cls.encounter,
            consultation_fee="2000.00", created_by=cls.users[Role.BILLING_OFFICER],
        )

    def auth_as(self, role):
        """Log in as the given role and attach the JWT to the client."""
        response = self.client.post("/api/auth/login/", {
            "username": f"test_{role.lower()}", "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class LaboratoryResultBoundaryTests(RBACBoundaryTestCase):
    """Only Lab Tech may write Laboratory_Result. Doctor and Nurse can order, not resu lt."""

    def _payload(self):
        return {
            "order": str(self.lab_order.id),
            "result_value": "4.5", "unit": "x10^9/L",
            "reference_range": "4.0-11.0", "is_abnormal": False,
        }

    def test_lab_tech_can_write_result(self):
        self.auth_as(Role.LAB_TECH)
        response = self.client.post("/api/laboratory/results/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_doctor_cannot_write_result(self):
        self.auth_as(Role.DOCTOR)
        response = self.client.post("/api/laboratory/results/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nurse_cannot_write_result(self):
        self.auth_as(Role.NURSE)
        response = self.client.post("/api/laboratory/results/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacist_cannot_write_result(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.post("/api/laboratory/results/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_write_result(self):
        """Hierarchical tier — Super Admin passes every boundary."""
        self.auth_as(Role.SUPER_ADMIN)
        response = self.client.post("/api/laboratory/results/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)


class DispensingBoundaryTests(RBACBoundaryTestCase):
    """Only Pharmacist may create a Dispensing_Record. Doctor prescribes, does not dispense."""

    def _payload(self):
        return {"prescription": str(self.prescription.id), "quantity_dispensed": 10}

    def test_pharmacist_can_dispense(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.post("/api/pharmacy/dispensing-records/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_doctor_cannot_dispense(self):
        self.auth_as(Role.DOCTOR)
        response = self.client.post("/api/pharmacy/dispensing-records/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nurse_cannot_dispense(self):
        self.auth_as(Role.NURSE)
        response = self.client.post("/api/pharmacy/dispensing-records/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lab_tech_cannot_dispense(self):
        self.auth_as(Role.LAB_TECH)
        response = self.client.post("/api/pharmacy/dispensing-records/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ClinicalWriteBoundaryTests(RBACBoundaryTestCase):
    """Doctor and Nurse may write Encounters. Lab Tech, Pharmacist, Billing Officer may not."""

    def _payload(self):
        return {
            "patient": str(self.patient.id), "department": str(self.department.id),
            "chief_complaint": "Follow-up visit",
        }

    def test_doctor_can_write_encounter(self):
        self.auth_as(Role.DOCTOR)
        response = self.client.post("/api/clinical/encounters/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_nurse_can_write_encounter(self):
        self.auth_as(Role.NURSE)
        response = self.client.post("/api/clinical/encounters/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_lab_tech_cannot_write_encounter(self):
        self.auth_as(Role.LAB_TECH)
        response = self.client.post("/api/clinical/encounters/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacist_cannot_write_encounter(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.post("/api/clinical/encounters/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_billing_officer_cannot_write_encounter(self):
        self.auth_as(Role.BILLING_OFFICER)
        response = self.client.post("/api/clinical/encounters/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BillingBoundaryTests(RBACBoundaryTestCase):
    """Only Billing Officer (and admin tier) may write Invoices/Payments."""

    def _invoice_payload(self):
        return {"patient": str(self.patient.id), "consultation_fee": "1500.00"}

    def test_billing_officer_can_write_invoice(self):
        self.auth_as(Role.BILLING_OFFICER)
        response = self.client.post("/api/billing/invoices/", self._invoice_payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_doctor_cannot_write_invoice(self):
        self.auth_as(Role.DOCTOR)
        response = self.client.post("/api/billing/invoices/", self._invoice_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nurse_cannot_write_invoice(self):
        self.auth_as(Role.NURSE)
        response = self.client.post("/api/billing/invoices/", self._invoice_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacist_cannot_write_invoice(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.post("/api/billing/invoices/", self._invoice_payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_any_authenticated_role_can_read_invoices(self):
        """Read access is intentionally broad — billing status visibility is not sensitive."""
        self.auth_as(Role.DOCTOR)
        response = self.client.get("/api/billing/invoices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PatientRegistrationBoundaryTests(RBACBoundaryTestCase):
    """Admin tier + Nurse may register patients. Lab Tech, Pharmacist, Billing Officer may not."""

    def _payload(self):
        return {
            "first_name": "John", "last_name": "Smith",
            "date_of_birth": "1985-05-20", "gender": "M",
        }

    def test_admin_can_register_patient(self):
        self.auth_as(Role.ADMIN)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_nurse_can_register_patient(self):
        self.auth_as(Role.NURSE)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

    def test_doctor_cannot_register_patient(self):
        """Doctors read patient records but registration is a front-desk/nursing task."""
        self.auth_as(Role.DOCTOR)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lab_tech_cannot_register_patient(self):
        self.auth_as(Role.LAB_TECH)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacist_cannot_register_patient(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_billing_officer_cannot_register_patient(self):
        self.auth_as(Role.BILLING_OFFICER)
        response = self.client.post("/api/patients/patients/", self._payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_authenticated_staff_can_read_patients(self):
        self.auth_as(Role.PHARMACIST)
        response = self.client.get("/api/patients/patients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardAccessBoundaryTests(RBACBoundaryTestCase):
    """Admin dashboard: Admin tier only, per the existing test we ran manually earlier."""

    def test_admin_can_access_dashboard(self):
        self.auth_as(Role.ADMIN)
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_can_access_dashboard(self):
        self.auth_as(Role.SUPER_ADMIN)
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_cannot_access_dashboard(self):
        self.auth_as(Role.DOCTOR)
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_billing_officer_cannot_access_dashboard(self):
        self.auth_as(Role.BILLING_OFFICER)
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnauthenticatedAccessTests(RBACBoundaryTestCase):
    """Baseline: no token at all must be rejected everywhere, not just role-gated endpoints."""

    def test_unauthenticated_request_rejected(self):
        response = self.client.get("/api/patients/patients/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_write_lab_result(self):
        response = self.client.post("/api/laboratory/results/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
