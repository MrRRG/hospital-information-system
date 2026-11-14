from django.core.management.base import BaseCommand

from accounts.models import User
from patients.models import Patient
from visits.models import Visit


class Command(BaseCommand):
    help = "Create a few FAKE visits for testing."

    def handle(self, *args, **options):
        doctor = User.objects.filter(role="doctor").first()
        if not doctor or Visit.objects.exists():
            self.stdout.write("Skipped (no doctor, or visits already exist).")
            return
        rows = [("Persistent cough", 37.2, 120, 80, 78, 70.5, "Upper respiratory infection", "Rest, fluids, review in 1 week"),
                ("Headache", 36.8, 135, 88, 82, 82.0, "Tension headache", "Paracetamol as needed"),
                ("Routine diabetes follow-up", 36.6, 128, 82, 74, 91.3, "Type 2 diabetes, stable", "Continue current plan"),
                ("Chest pain", 37.0, 142, 92, 96, 77.8, "Under investigation", "ECG and blood tests ordered")]
        for p, r in zip(Patient.objects.all()[:4], rows):
            Visit.objects.create(patient=p, doctor=doctor, created_by=doctor, complaint=r[0], temperature=r[1],
                                 systolic=r[2], diastolic=r[3], heart_rate=r[4], weight_kg=r[5],
                                 diagnosis=r[6], treatment_plan=r[7])
        self.stdout.write(self.style.SUCCESS("4 fake visits created."))
