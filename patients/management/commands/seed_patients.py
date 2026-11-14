import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from patients.models import Patient

FIRST = ["Ahmed", "Mohammed", "Khalid", "Fahad", "Saud", "Noura", "Huda", "Reem", "Maha", "Layla"]
LAST = ["Al-Ali", "Al-Harbi", "Al-Otaibi", "Al-Qahtani", "Al-Mutairi", "Al-Dosari"]
BLOOD = ["A+", "B+", "O+", "O-", "AB+", "A-"]


class Command(BaseCommand):
    help = "Create 15 FAKE patients for testing. Never put real patient data in the prototype."

    def handle(self, *args, **options):
        random.seed(7)
        made = 0
        for i in range(15):
            nid = f"1{100000000 + i * 137:09d}"
            _, created = Patient.objects.get_or_create(
                national_id=nid,
                defaults=dict(
                    first_name=random.choice(FIRST), last_name=random.choice(LAST),
                    date_of_birth=date(1940, 1, 1) + timedelta(days=random.randint(0, 25000)),
                    gender=random.choice(["M", "F"]), phone=f"05{random.randint(10000000, 99999999)}",
                    blood_type=random.choice(BLOOD),
                    allergies=random.choice(["", "", "Penicillin", "Latex"]),
                    chronic_conditions=random.choice(["", "Diabetes", "Hypertension", "Asthma"]),
                ),
            )
            made += created
        self.stdout.write(self.style.SUCCESS(f"{made} fake patients created."))
