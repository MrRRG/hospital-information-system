from datetime import time

from django.conf import settings
from django.db import models
from django.db.models import Q

# Clinic runs 08:00 to 16:00 in 30-minute slots (last slot 15:30).
SLOTS = [(time(h, m), f"{h:02d}:{m:02d}") for h in range(8, 16) for m in (0, 30)]


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CHECKED_IN = "checked_in", "Checked in"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No-show"

    # Which status can follow which. Completed, cancelled and no-show are final.
    TRANSITIONS = {
        "scheduled": {"checked_in", "cancelled", "no_show"},
        "checked_in": {"completed"},
    }

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                               limit_choices_to={"role": "doctor"}, related_name="appointments")
    date = models.DateField()
    start_time = models.TimeField(choices=SLOTS)
    reason = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="appointments_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            # Database-level guard: a doctor cannot have two active appointments in one slot.
            models.UniqueConstraint(
                fields=["doctor", "date", "start_time"],
                condition=~Q(status__in=["cancelled", "no_show"]),
                name="no_double_booking_per_doctor",
            )
        ]

    def can_change_to(self, new_status):
        return new_status in self.TRANSITIONS.get(self.status, set())

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor} on {self.date} {self.start_time:%H:%M}"
