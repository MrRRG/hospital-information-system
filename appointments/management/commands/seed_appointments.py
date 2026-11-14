from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from accounts.models import User
from appointments.models import Appointment
from patients.models import Patient


class Command(BaseCommand):
    help = "Create a few FAKE appointments for today and tomorrow (needs seed_demo and seed_patients first)."

    def handle(self, *args, **options):
        doctors = list(User.objects.filter(role="doctor"))
        patients = list(Patient.objects.all()[:8])
        if not doctors or len(patients) < 8:
            self.stdout.write("Run seed_demo and seed_patients first.")
            return
        reasons = ["Follow-up", "Check-up", "Lab results review", "New complaint"]
        made = 0
        for i, p in enumerate(patients):
            _, c = Appointment.objects.get_or_create(
                doctor=doctors[i % len(doctors)], date=date.today() + timedelta(days=i // 5),
                start_time=time(8 + (i % 5), 0 if i % 2 == 0 else 30),
                defaults=dict(patient=p, reason=reasons[i % 4]),
            )
            made += c
        self.stdout.write(self.style.SUCCESS(f"{made} fake appointments created."))
