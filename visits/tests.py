from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from appointments.models import Appointment
from audit.models import AuditLog
from patients.models import Patient

from .models import Visit


class VisitAndAuditTests(TestCase):
    def setUp(self):
        self.doc = User.objects.create_user("d", password="x", role="doctor", first_name="Sara")
        self.nurse = User.objects.create_user("n", password="x", role="nurse")
        self.recep = User.objects.create_user("r", password="x", role="receptionist")
        self.admin = User.objects.create_superuser("a", password="x")
        self.p = Patient.objects.create(national_id="1012345678", first_name="Test", last_name="Patient",
                                        date_of_birth=date(1990, 1, 1), gender="M")

    def test_receptionist_cannot_open_visits(self):
        self.client.login(username="r", password="x")
        self.assertEqual(self.client.get(reverse("visit_list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("visit_create") + f"?patient={self.p.pk}").status_code, 403)

    def test_nurse_form_has_no_diagnosis_but_doctor_form_has(self):
        self.client.login(username="n", password="x")
        self.assertNotContains(self.client.get(reverse("visit_create") + f"?patient={self.p.pk}"), "diagnosis")
        self.client.login(username="d", password="x")
        self.assertContains(self.client.get(reverse("visit_create") + f"?patient={self.p.pk}"), "diagnosis")

    def test_nurse_vitals_then_doctor_diagnosis(self):
        self.client.login(username="n", password="x")
        r = self.client.post(reverse("visit_create") + f"?patient={self.p.pk}",
                             {"complaint": "Fever", "temperature": "38.5", "systolic": "120", "diastolic": "80"})
        v = Visit.objects.get()
        self.assertRedirects(r, reverse("visit_detail", args=[v.pk]))
        self.assertEqual(v.blood_pressure, "120/80")
        self.client.login(username="d", password="x")
        self.client.post(reverse("visit_edit", args=[v.pk]), {"complaint": "Fever", "temperature": "38.5",
                         "systolic": "120", "diastolic": "80", "diagnosis": "Flu"})
        v.refresh_from_db()
        self.assertEqual((v.diagnosis, v.doctor), ("Flu", self.doc))

    def test_bad_vitals_rejected(self):
        self.client.login(username="d", password="x")
        r = self.client.post(reverse("visit_create") + f"?patient={self.p.pk}",
                             {"complaint": "x", "systolic": "80", "diastolic": "120"})
        self.assertContains(r, "Systolic must be higher")
        self.assertEqual(Visit.objects.count(), 0)

    def test_visit_from_checked_in_appointment_completes_it(self):
        a = Appointment.objects.create(patient=self.p, doctor=self.doc, date=date.today(),
                                       start_time=time(9, 0), status="checked_in", reason="Check-up")
        self.client.login(username="d", password="x")
        self.client.post(reverse("visit_create") + f"?appointment={a.pk}", {"complaint": "Check-up"})
        a.refresh_from_db()
        self.assertEqual(a.status, "completed")
        self.assertEqual(a.visit.doctor, self.doc)

    def test_opening_a_patient_is_audited(self):
        self.client.login(username="d", password="x")
        self.client.get(reverse("patient_detail", args=[self.p.pk]))
        log = AuditLog.objects.filter(action="view").latest("timestamp")
        self.assertEqual((log.username, log.target), ("d", f"Patient {self.p.mrn}"))

    def test_login_and_failed_login_are_audited(self):
        self.client.post(reverse("login"), {"username": "d", "password": "wrong"})
        self.client.post(reverse("login"), {"username": "d", "password": "x"})
        actions = set(AuditLog.objects.values_list("action", flat=True))
        self.assertTrue({"login_failed", "login"} <= actions)

    def test_audit_page_admin_only_and_dashboard_stats(self):
        self.client.login(username="d", password="x")
        self.assertEqual(self.client.get(reverse("audit_list")).status_code, 403)
        self.client.login(username="a", password="x")
        self.assertEqual(self.client.get(reverse("audit_list")).status_code, 200)
        self.assertContains(self.client.get(reverse("dashboard")), "Patients registered")
