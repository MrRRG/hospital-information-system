from django.core.management.base import BaseCommand

from accounts.models import User

DEMO_PASSWORD = "Demo@12345"  # demo only - never use in a real system

DEMO_USERS = [
    ("admin_demo", "Admin", "User", "admin"),
    ("doctor_demo", "Dr. Sara", "Demo", "doctor"),
    ("doctor2_demo", "Dr. Omar", "Demo", "doctor"),
    ("nurse_demo", "Nurse Huda", "Demo", "nurse"),
    ("reception_demo", "Reception", "Demo", "receptionist"),
]


class Command(BaseCommand):
    help = "Create demo users (fake data only) for testing the HIS."

    def handle(self, *args, **options):
        for username, first, last, role in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "role": role},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.is_staff = role == "admin"
                user.save()
            self.stdout.write(f"{'created' if created else 'exists '}  {username}  ({role})")
        self.stdout.write(self.style.SUCCESS(f"Done. Demo password: {DEMO_PASSWORD}"))
