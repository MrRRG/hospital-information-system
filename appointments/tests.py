from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from patients.models import Patient

from .models import Appointment


def make_patient(nid="1012345678"):
    return Patient.objects.create(national_id=nid, first_name="Test", last_name="Patient",
                                  date_of_birth=date(1990, 1, 1), gender="F")


class AppointmentTests(TestCase):
    def setUp(self):
        self.recep = User.objects.create_user("r", password="x", role="receptionist")
        self.doc = User.objects.create_user("d", password="x", role="doctor", first_name="Sara")
        self.doc2 = User.objects.create_user("d2", password="x", role="doctor", first_name="Omar")
        self.nurse = User.objects.create_user("n", password="x", role="nurse")
        self.p = make_patient()
        self.tomorrow = date.today() + timedelta(days=1)

    def book(self, **kw):
        data = dict(patient=self.p.pk, doctor=self.doc.pk, date=self.tomorrow.isoformat(),
                    start_time="09:00:00", reason="Check-up")
        data.update(kw)
        return self.client.post(reverse("appointment_create"), data)

    def test_nurse_has_no_access(self):
        self.client.login(username="n", password="x")
        self.assertEqual(self.client.get(reverse("appointment_list")).status_code, 403)

    def test_book_and_block_double_booking(self):
        self.client.login(username="r", password="x")
        self.assertEqual(self.book().status_code, 302)
        r = self.book()  # same doctor, same slot
        self.assertContains(r, "already has an appointment")
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(self.book(doctor=self.doc2.pk).status_code, 302)  # other doctor is fine

    def test_cancelled_slot_can_be_rebooked(self):
        self.client.login(username="r", password="x")
        self.book()
        a = Appointment.objects.get()
        self.client.post(reverse("appointment_status", args=[a.pk, "cancelled"]))
        self.assertEqual(self.book().status_code, 302)

    def test_past_date_rejected(self):
        self.client.login(username="r", password="x")
        r = self.book(date=(date.today() - timedelta(days=1)).isoformat())
        self.assertContains(r, "today or a future date")

    def test_doctor_sees_only_own_and_completes_after_checkin(self):
        a = Appointment.objects.create(patient=self.p, doctor=self.doc, date=date.today(), start_time=time(9, 0))
        Appointment.objects.create(patient=make_patient("1087654321"), doctor=self.doc2,
                                   date=date.today(), start_time=time(10, 0))
        self.client.login(username="d", password="x")
        page = self.client.get(reverse("appointment_list"))
        self.assertEqual(len(page.context["items"]), 1)
        # cannot complete before check-in
        self.client.post(reverse("appointment_status", args=[a.pk, "completed"]))
        a.refresh_from_db(); self.assertEqual(a.status, "scheduled")
        # doctor cannot check in (reception does that)
        self.assertEqual(self.client.post(reverse("appointment_status", args=[a.pk, "checked_in"])).status_code, 403)
        self.client.login(username="r", password="x")
        self.client.post(reverse("appointment_status", args=[a.pk, "checked_in"]))
        self.client.login(username="d", password="x")
        self.client.post(reverse("appointment_status", args=[a.pk, "completed"]))
        a.refresh_from_db(); self.assertEqual(a.status, "completed")
