from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create ALL demo data (fake users, patients, appointments, visits) in the right order."

    def handle(self, *args, **options):
        for name in ("seed_demo", "seed_patients", "seed_appointments", "seed_visits"):
            call_command(name)
