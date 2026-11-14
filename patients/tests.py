from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Patient

DATA = dict(national_id="1012345678", first_name="Test", last_name="Patient",
            date_of_birth="1980-05-01", gender="M", phone="0500000000", address="")


class PatientTests(TestCase):
    def setUp(self):
        self.recep = User.objects.create_user("r", password="x", role="receptionist")
        self.doc = User.objects.create_user("d", password="x", role="doctor")

    def test_login_required(self):
        self.assertEqual(self.client.get(reverse("patient_list")).status_code, 302)

    def test_receptionist_registers_without_medical_fields(self):
        self.client.login(username="r", password="x")
        form_page = self.client.get(reverse("patient_create"))
        self.assertNotContains(form_page, "allergies")
        r = self.client.post(reverse("patient_create"), DATA)
        p = Patient.objects.get()
        self.assertRedirects(r, reverse("patient_detail", args=[p.pk]))
        self.assertEqual(p.mrn, f"P-{p.pk:06d}")
        self.assertEqual(p.created_by, self.recep)

    def test_medical_info_hidden_from_receptionist(self):
        p = Patient.objects.create(**{**DATA, "date_of_birth": date(1980, 5, 1)}, allergies="Penicillin")
        self.client.login(username="r", password="x")
        self.assertNotContains(self.client.get(reverse("patient_detail", args=[p.pk])), "Penicillin")
        self.client.login(username="d", password="x")
        self.assertContains(self.client.get(reverse("patient_detail", args=[p.pk])), "Penicillin")

    def test_bad_national_id_rejected(self):
        self.client.login(username="d", password="x")
        r = self.client.post(reverse("patient_create"), {**DATA, "national_id": "999"})
        self.assertEqual(Patient.objects.count(), 0)
        self.assertContains(r, "10-digit")

    def test_search(self):
        Patient.objects.create(**{**DATA, "date_of_birth": date(1980, 5, 1)})
        self.client.login(username="d", password="x")
        self.assertContains(self.client.get(reverse("patient_list"), {"q": "Patient"}), "Test Patient")
        self.assertNotContains(self.client.get(reverse("patient_list"), {"q": "zzz"}), "Test Patient")
