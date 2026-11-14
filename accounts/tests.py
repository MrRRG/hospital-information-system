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


class LanguageTests(TestCase):
    def test_default_is_english_ltr(self):
        r = self.client.get(reverse("login"))
        self.assertContains(r, 'dir="ltr"')
        self.assertContains(r, "Welcome back")

    def test_switch_to_arabic_and_back(self):
        r = self.client.post("/i18n/setlang/", {"language": "ar", "next": "/login/"}, follow=True)
        self.assertContains(r, 'dir="rtl"')
        self.assertContains(r, "أهلاً بعودتك")
        r = self.client.post("/i18n/setlang/", {"language": "en", "next": "/login/"}, follow=True)
        self.assertContains(r, "Welcome back")

    def test_dashboard_in_arabic(self):
        User.objects.create_user("n", password="x", role="nurse")
        self.client.login(username="n", password="x")
        self.client.post("/i18n/setlang/", {"language": "ar", "next": "/"})
        r = self.client.get("/")
        self.assertContains(r, "المرضى")
        self.assertContains(r, "ممرض")
        self.assertNotContains(r, "Audit log")
