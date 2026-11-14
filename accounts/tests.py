from django.test import TestCase
from django.urls import reverse

from .models import User


class AccessTests(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user("d", password="x", role="doctor")
        self.recep = User.objects.create_user("r", password="x", role="receptionist")

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_login_and_role_modules(self):
        self.client.login(username="r", password="x")
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "Appointments")
        self.assertNotContains(r, "Audit log")

    def test_audit_only_for_admin(self):
        admin = User.objects.create_superuser("a", password="x")
        self.assertEqual(admin.role, "admin")
        self.client.login(username="a", password="x")
        self.assertContains(self.client.get(reverse("dashboard")), "Audit log")
